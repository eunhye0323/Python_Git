import json
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from quiz_game import PROJECT_ROOT, QuizGame, main


class QuizGameTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.app = self.root / "game"
        self.app.mkdir()
        for name in ("quiz_game.py", "quiz.py", "quiz_storage.py", "quiz_list.json"):
            shutil.copy2(PROJECT_ROOT / name, self.app)
        self.state = self.app / "state.json"
        self.question = {"question": "테스트 문제?", "choices": ["가", "나", "다", "라"], "answer": 2}

    def run_game(self, *lines):
        result = subprocess.run(
            [sys.executable, str(self.app / "quiz_game.py")],
            cwd=self.root, input="".join(line + "\n" for line in lines),
            text=True, encoding="utf-8", capture_output=True, timeout=5, check=True,
        )
        self.assertEqual(result.stderr, "")
        return result.stdout

    def read_state(self):
        return json.loads(self.state.read_text(encoding="utf-8"))

    def seed_one(self, **fields):
        state = {"quizzes": [dict(self.question, **fields)], "best_score": None}
        self.state.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def test_first_launch_and_menu_retry_outside_project(self):
        output = self.run_game("", "abc", "9", " 3 ", "4", "5")
        self.assertEqual(output.count("1~6 사이의 숫자"), 3)
        self.assertIn("아직 퀴즈를 끝까지 푼 기록이 없습니다.", output)
        quizzes = self.read_state()["quizzes"]
        self.assertGreaterEqual(len(quizzes), 5)
        for quiz in quizzes:
            self.assertIn(quiz["question"], output)
            self.assertEqual(len(quiz["choices"]), 4)
            self.assertIn(quiz["answer"], range(1, 5))
            self.assertTrue(quiz["hint"])
        self.assertFalse((self.root / "state.json").exists())

    def test_add_cancel_delete_and_restart(self):
        self.seed_one()
        output = self.run_game("2", " ", " 새 문제 ", "", " 하나 ", "둘", "셋", "넷",
                               "abc", "0", " 4 ", "", "5")
        self.assertEqual(output.count("내용을 한 글자 이상"), 2)
        self.assertEqual(output.count("1~4 사이의 숫자"), 2)
        added = self.read_state()["quizzes"][-1]
        self.assertEqual((added["question"], added["choices"], added["answer"], added["hint"]),
                         ("새 문제", ["하나", "둘", "셋", "넷"], 4, ""))
        self.assertIn("2. 새 문제", self.run_game("3", "6", "0", "5"))
        self.assertEqual(len(self.read_state()["quizzes"]), 2)
        self.run_game("6", "3", "2", "6", "1", "5")
        output = self.run_game("3", "1", "6", "5")
        self.assertIn("풀 수 있는 퀴즈가 없습니다.", output)
        self.assertIn("등록된 퀴즈가 없습니다.", output)
        self.assertEqual(self.read_state()["quizzes"], [])

    def test_hint_cost_best_and_history_across_restarts(self):
        self.seed_one(hint="두 번째")
        self.run_game("1", "", "2", "1", " H ", "힌트", "0", " 2 ", "5")
        record = self.read_state()["history"][0]
        self.assertEqual((record["total"], record["hints_used"], record["score"]), (1, 1, 50))
        self.run_game("1", "1", "2", "1", "1", "h", "1", "5")
        output = self.run_game("4", "5")
        state = self.read_state()
        self.assertEqual(state["best_score"], 100)
        self.assertEqual([row["score"] for row in state["history"]], [50, 100, 0])
        self.assertIn("플레이 기록 3회 (최근 순)", output)
        self.assertIn("최고 점수: 100점", output)
        self.assertLess(output.index("| 0점"), output.index("| 50점"))

    def test_zero_score_and_absent_optional_hint(self):
        self.seed_one()
        self.run_game("1", "1", "h", "1", "5")
        self.assertIn("최고 점수: 0점", self.run_game("4", "5"))
        self.run_game("1", "1", "h", "2", "5")
        history = self.read_state()["history"]
        self.assertEqual([(r["score"], r["hints_used"]) for r in history], [(0, 0), (100, 0)])

    def test_random_round_uses_requested_number_of_distinct_questions(self):
        output = self.run_game("1", "3", "1", "1", "1", "5")
        state = self.read_state()
        asked = [quiz for quiz in state["quizzes"] if quiz["question"] in output]
        self.assertEqual(len(asked), 3)
        self.assertEqual(state["history"][0]["total"], 3)

    def test_bad_encoding_json_or_fields_restore_defaults(self):
        invalid_states = (b"\xff", b"{", b"[]", b'{"quizzes":[{}],"best_score":null}',
                          b'{"quizzes":[],"best_score":true}', b'{"quizzes":[],"best_score":0,"history":[{}]}')
        for invalid in invalid_states:
            with self.subTest(invalid=invalid):
                self.state.write_bytes(invalid)
                self.assertIn("손상", self.run_game("5"))
                state = self.read_state()
                self.assertGreaterEqual(len(state["quizzes"]), 5)
                self.assertEqual((state["best_score"], state["history"]), (None, []))

    def test_eof_and_interrupt_discard_unfinished_inputs(self):
        self.run_game("1", "2", "1")
        state = self.read_state()
        self.assertEqual(state["history"], [])
        self.assertIn("입력이 중단되었습니다.", self.run_game("2", "미완성 문제", "첫 선택지"))
        game = QuizGame(self.state)
        with patch("quiz_game.QuizGame", return_value=game), redirect_stdout(StringIO()) as stream:
            with patch("builtins.input", side_effect=["1", "2", "2", KeyboardInterrupt()]):
                main()
        self.assertIn("입력이 중단되었습니다.", stream.getvalue())
        self.assertEqual(self.read_state(), state)

    def test_interrupted_write_preserves_previous_file_and_can_retry(self):
        self.seed_one()
        original = self.state.read_bytes()
        game = QuizGame(self.state)
        with redirect_stdout(StringIO()) as stream:
            game.load_state()
            with patch.object(Path, "replace", side_effect=OSError("쓰기 실패")):
                game.finish_round(1, 1, 0)
            self.assertEqual(self.state.read_bytes(), original)
            self.assertEqual(list(self.app.glob(".state-*.tmp")), [])
            game.save_state()
        self.assertIn("저장하지 못했습니다", stream.getvalue())
        self.assertEqual(len(self.read_state()["history"]), 1)

    def test_two_sessions_keep_each_others_questions_and_scores(self):
        self.seed_one()
        first, second = QuizGame(self.state), QuizGame(self.state)
        with redirect_stdout(StringIO()):
            first.load_state()
            second.load_state()
            with patch("builtins.input", side_effect=["추가 문제", "가", "나", "다", "라", "1", ""]):
                first.add_quiz()
            with patch("builtins.input", return_value="1"):
                second.delete_quiz()
            first.finish_round(1, 1, 0)
            second.finish_round(1, 0, 0)
        state = self.read_state()
        self.assertEqual([q["question"] for q in state["quizzes"]], ["추가 문제"])
        self.assertEqual([r["score"] for r in state["history"]], [100, 0])
        self.assertEqual(state["best_score"], 100)

    def test_unreadable_state_starts_without_overwriting_it(self):
        self.state.mkdir()
        output = self.run_game("3", "5")
        self.assertIn("저장 파일을 읽을 수 없습니다.", output)
        self.assertIn("총 5개", output)
        self.assertTrue(self.state.is_dir())


if __name__ == "__main__":
    unittest.main()

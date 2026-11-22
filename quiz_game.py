import random
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from quiz import Quiz
from quiz_storage import decode_quizzes, decode_state, read_json, write_json


PROJECT_ROOT = Path(__file__).resolve().parent
SEED_FILE = PROJECT_ROOT / "quiz_list.json"
STATE_FILE = PROJECT_ROOT / "state.json"


def parse_number(text: str, minimum: int, maximum: int) -> int | None:
    try:
        number = int(text.strip())
    except ValueError:
        pass
    else:
        if minimum <= number <= maximum:
            return number
    print(f"{minimum}~{maximum} 사이의 숫자를 입력해 주세요.")
    return None


def read_number(prompt: str, minimum: int, maximum: int) -> int:
    while True:
        number = parse_number(input(prompt), minimum, maximum)
        if number is not None:
            return number


def read_text(prompt: str) -> str:
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("내용을 한 글자 이상 입력해 주세요.")


class QuizGame:
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.quizzes: list[Quiz] = []
        self.best_score: int | None = None
        self.history: list[dict] = []
        self.dirty = False
        self.can_save = True

    def load_state(self) -> None:
        try:
            self.quizzes, self.best_score, self.history = decode_state(read_json(self.state_file))
        except FileNotFoundError:
            print("첫 실행입니다. 기본 퀴즈를 불러옵니다.")
        except (ValueError, RecursionError) as error:
            print(f"저장 데이터가 손상되었습니다. 기본 퀴즈로 복구합니다. ({error})")
        except OSError as error:
            self.can_save = False
            print(f"저장 파일을 읽을 수 없습니다. 이번 실행의 변경은 메모리에만 유지됩니다. ({error})")
        else:
            print(f"저장된 퀴즈 {len(self.quizzes)}개를 불러왔습니다.")
            return

        try:
            self.quizzes = decode_quizzes(read_json(SEED_FILE))
        except (OSError, ValueError, RecursionError) as error:
            print(f"기본 퀴즈를 읽을 수 없습니다. 빈 목록으로 시작합니다. ({error})")
            return
        self.dirty = True
        self.save_state()

    def save_state(self) -> None:
        if not self.dirty or not self.can_save:
            return
        data = {
            "quizzes": [asdict(quiz) for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        try:
            write_json(self.state_file, data)
        except (OSError, UnicodeError) as error:
            print(f"저장하지 못했습니다. ({error})")
        else:
            self.dirty = False

    def list_quizzes(self) -> None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        print(f"\n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"  {number}. {quiz.question}")

    def add_quiz(self) -> None:
        print("\n새 퀴즈 등록")
        question = read_text("문제: ")
        choices = [read_text(f"선택지 {number}: ") for number in range(1, 5)]
        answer = read_number("정답 번호 (1~4): ", 1, 4)
        hint = input("힌트 (없으면 Enter): ").strip()
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.dirty = True
        print(f"퀴즈를 추가했습니다. 현재 {len(self.quizzes)}개입니다.")
        self.save_state()

    def delete_quiz(self) -> None:
        self.list_quizzes()
        if not self.quizzes:
            return
        number = read_number("삭제할 문제 번호 (0=취소): ", 0, len(self.quizzes))
        if number == 0:
            print("삭제를 취소했습니다.")
            return
        removed = self.quizzes.pop(number - 1)
        self.dirty = True
        print(f"삭제했습니다: {removed.question}")
        self.save_state()

    def ask_question(self, quiz: Quiz) -> tuple[bool, bool]:
        quiz.display()
        used_hint = False
        while True:
            text = input("정답 번호 (1~4, h=힌트): ").strip()
            if text.lower() in ("h", "힌트"):
                if quiz.hint:
                    print(f"힌트: {quiz.hint}")
                    used_hint = True
                else:
                    print("등록된 힌트가 없습니다. 점수 차감은 없습니다.")
                continue
            answer = parse_number(text, 1, 4)
            if answer is not None:
                break
        correct = quiz.check_answer(answer)
        if correct:
            print("정답입니다!")
        else:
            print(f"오답입니다. 정답은 {quiz.answer}번 ({quiz.choices[quiz.answer - 1]})입니다.")
        return correct, used_hint

    def play(self) -> None:
        if not self.quizzes:
            print("풀 수 있는 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return
        available = len(self.quizzes)
        count = read_number(f"풀 문제 수 (1~{available}): ", 1, available)
        selected = random.sample(self.quizzes, count)
        print("정답은 2점, 힌트를 열면 문제당 한 번 1점 차감합니다. 결과는 100점으로 환산합니다.")
        correct = 0
        hints_used = 0
        for index, quiz in enumerate(selected, start=1):
            print(f"\n[문제 {index}/{count}]")
            is_correct, used_hint = self.ask_question(quiz)
            correct += is_correct
            hints_used += used_hint
        self.finish_round(count, correct, hints_used)

    def finish_round(self, count: int, correct: int, hints_used: int) -> None:
        points = max(0, 2 * correct - hints_used)
        score = round(100 * points / (2 * count))
        print(f"\n결과: {count}문제 중 {correct}문제 정답 · 힌트 {hints_used}회 · {score}점")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("새로운 최고 점수입니다!")
        self.history.append({
            "played_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "total": count,
            "correct": correct,
            "hints_used": hints_used,
            "score": score,
        })
        self.dirty = True
        self.save_state()

    def show_scores(self) -> None:
        if self.best_score is None:
            print("아직 퀴즈를 끝까지 푼 기록이 없습니다.")
            return
        print(f"\n최고 점수: {self.best_score}점")
        if not self.history:
            print("회차별 기록이 없습니다.")
            return
        print(f"플레이 기록 {len(self.history)}회 (최근 순)")
        for record in reversed(self.history):
            when = record["played_at"].replace("T", " ", 1)
            print(f"  {when} | {record['total']}문제 중 {record['correct']}문제 정답"
                  f" | 힌트 {record['hints_used']}회 | {record['score']}점")

    def show_menu(self) -> None:
        print("\n기술 퀴즈 | 메뉴")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 최고 점수와 플레이 기록")
        print("5. 종료")
        print("6. 퀴즈 삭제")

    def start(self) -> None:
        while True:
            self.show_menu()
            choice = read_number("메뉴 선택 (1~6): ", 1, 6)
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_scores()
            elif choice == 5:
                return
            else:
                self.delete_quiz()


def main() -> None:
    game = QuizGame()
    try:
        game.load_state()
        game.start()
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 중단되었습니다.")
    game.save_state()
    print("퀴즈 게임을 종료합니다.")


if __name__ == "__main__":
    main()

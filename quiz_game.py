from dataclasses import asdict
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


class QuizGame:
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.quizzes: list[Quiz] = []
        self.best_score: int | None = None
        self.dirty = False
        self.can_save = True

    def load_state(self) -> None:
        try:
            self.quizzes, self.best_score = decode_state(read_json(self.state_file))
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
        data = {"quizzes": [asdict(quiz) for quiz in self.quizzes], "best_score": self.best_score}
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

    def show_menu(self) -> None:
        print("\n기술 퀴즈 | 메뉴")
        print("3. 퀴즈 목록")
        print("5. 종료")

    def start(self) -> None:
        while True:
            self.show_menu()
            choice = read_number("메뉴 선택: ", 3, 5)
            if choice == 3:
                self.list_quizzes()
            elif choice == 5:
                return
            else:
                print("메뉴에서 번호를 선택해 주세요.")


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

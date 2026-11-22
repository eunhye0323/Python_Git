import json
from pathlib import Path

from quiz import Quiz


PROJECT_ROOT = Path(__file__).resolve().parent
SEED_FILE = PROJECT_ROOT / "quiz_list.json"


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
    def __init__(self):
        self.quizzes: list[Quiz] = []

    def load_quizzes(self) -> None:
        with SEED_FILE.open(encoding="utf-8") as file:
            self.quizzes = [Quiz.from_dict(item) for item in json.load(file)]

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
        game.load_quizzes()
        game.start()
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 중단되어 게임을 종료합니다.")
    print("퀴즈 게임을 종료합니다.")


if __name__ == "__main__":
    main()

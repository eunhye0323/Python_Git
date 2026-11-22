from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Quiz:
    question: str
    choices: list[str]
    answer: int
    hint: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        if not isinstance(data, dict):
            raise ValueError("각 퀴즈는 JSON 객체여야 합니다.")
        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        hint = data.get("hint", "")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("퀴즈의 문제 내용이 비어 있습니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("퀴즈마다 선택지가 4개 필요합니다.")
        if any(not isinstance(choice, str) or not choice.strip() for choice in choices):
            raise ValueError("퀴즈의 선택지에는 내용이 있어야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("퀴즈의 정답 번호는 1~4 사이의 정수여야 합니다.")
        if not isinstance(hint, str):
            raise ValueError("퀴즈의 힌트는 문자열이어야 합니다.")
        return cls(question.strip(), [choice.strip() for choice in choices], answer, hint.strip())

    def display(self) -> None:
        print(self.question)
        for number, choice in enumerate(self.choices, start=1):
            print(f"  {number}. {choice}")

    def check_answer(self, number: int) -> bool:
        return number == self.answer

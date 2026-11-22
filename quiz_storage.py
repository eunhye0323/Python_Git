import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from quiz import Quiz


def read_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def decode_quizzes(items: list) -> list[Quiz]:
    if not isinstance(items, list):
        raise ValueError("퀴즈 목록은 배열이어야 합니다.")
    return [Quiz.from_dict(item) for item in items]


def decode_state(data: dict) -> tuple[list[Quiz], int | None]:
    if not isinstance(data, dict) or "quizzes" not in data or "best_score" not in data:
        raise ValueError("quizzes 또는 best_score 필드가 없습니다.")
    best = data["best_score"]
    if best is not None and (type(best) is not int or not 0 <= best <= 100):
        raise ValueError("최고 점수는 0~100 사이의 정수여야 합니다.")
    return decode_quizzes(data["quizzes"]), best


def write_json(path: Path, data: dict) -> None:
    # 같은 폴더에서 쓰기를 끝낸 파일만 교체해 기존 기록이 반만 쓰이는 일을 막는다.
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".state-", suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

import json
from datetime import datetime
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


def validate_record(record: dict) -> None:
    if not isinstance(record, dict) or not isinstance(record.get("played_at"), str):
        raise ValueError("게임 기록에 날짜와 시간이 필요합니다.")
    datetime.fromisoformat(record["played_at"])
    total = record.get("total")
    if type(total) is not int or total < 1:
        raise ValueError("게임 기록의 문제 수는 양의 정수여야 합니다.")
    for key, maximum in (("correct", total), ("hints_used", total), ("score", 100)):
        value = record.get(key)
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(f"게임 기록의 {key} 값이 범위를 벗어났습니다.")


def decode_state(data: dict) -> tuple[list[Quiz], int | None, list[dict]]:
    if not isinstance(data, dict) or "quizzes" not in data or "best_score" not in data:
        raise ValueError("quizzes 또는 best_score 필드가 없습니다.")
    best = data["best_score"]
    if best is not None and (type(best) is not int or not 0 <= best <= 100):
        raise ValueError("최고 점수는 0~100 사이의 정수여야 합니다.")
    history = data.get("history", [])
    if not isinstance(history, list):
        raise ValueError("게임 기록은 배열이어야 합니다.")
    for record in history:
        validate_record(record)
    if history:
        best = max(best or 0, max(record["score"] for record in history))
    return decode_quizzes(data["quizzes"]), best, history


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

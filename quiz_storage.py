from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import asdict
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
    return decode_quizzes(data["quizzes"]), best, list(history)


def encode_state(quizzes: list[Quiz], best: int | None, history: list[dict]) -> dict:
    return {"quizzes": [asdict(quiz) for quiz in quizzes], "best_score": best, "history": list(history)}


@contextmanager
def lock_state(path: Path):
    # 파일을 닫으면 운영체제가 잠금을 해제한다. 입력을 기다리는 동안에는 잠그지 않는다.
    with path.with_name(f".{path.stem}.lock").open("a+b") as lock:
        if os.name == "nt":
            import msvcrt
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def merge_changes(latest: dict, previous: dict, current: dict) -> dict:
    # 이 게임에서 퀴즈는 추가·삭제만 되고, 완주 기록은 끝에만 추가된다.
    removed = previous["quizzes"].copy()
    for quiz in current["quizzes"]:
        if quiz in removed:
            removed.remove(quiz)
        else:
            latest["quizzes"].append(quiz)
    for quiz in removed:
        if quiz in latest["quizzes"]:
            latest["quizzes"].remove(quiz)
    latest["history"].extend(current["history"][len(previous["history"]):])
    best = current["best_score"]
    if best is not None and (latest["best_score"] is None or best > latest["best_score"]):
        latest["best_score"] = best
    return latest


def save_changes(path: Path, previous: dict, current: dict) -> dict:
    with lock_state(path):
        try:
            latest = encode_state(*decode_state(read_json(path)))
        except (FileNotFoundError, ValueError, RecursionError):
            latest = previous
        if latest != previous:
            current = merge_changes(latest, previous, current)
        write_json(path, current)
    return current


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

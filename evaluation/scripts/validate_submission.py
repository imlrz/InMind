#!/usr/bin/env python3
"""Validate the structural contract of an InMind system-output JSONL file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS = ROOT / "benchmark" / "dataset" / "inmind.jsonl"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            row["_line_number"] = line_number
            rows.append(row)
    return rows


def require_string(row: dict[str, Any], path: str, errors: list[str]) -> None:
    value: Any = row
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            errors.append(f"line {row['_line_number']}: missing {path}")
            return
        value = value[key]
    if not isinstance(value, str):
        errors.append(f"line {row['_line_number']}: {path} must be a string")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    task_rows = read_jsonl(args.tasks)
    expected_ids = {int(task["task_id"]) for task in task_rows}
    rows = read_jsonl(args.results)
    errors: list[str] = []
    seen: set[int] = set()

    for row in rows:
        task_id = row.get("task_id")
        if not isinstance(task_id, int):
            errors.append(f"line {row['_line_number']}: task_id must be an integer")
            continue
        if task_id not in expected_ids:
            errors.append(f"line {row['_line_number']}: unknown task_id={task_id}")
        if task_id in seen:
            errors.append(f"line {row['_line_number']}: duplicate task_id={task_id}")
        seen.add(task_id)

        require_string(row, "system", errors)
        if not isinstance(row.get("config"), dict):
            errors.append(f"line {row['_line_number']}: config must be an object")
        for field in ("naive.context", "naive.answer", "query.context", "query.answer"):
            require_string(row, field, errors)

    missing = expected_ids - seen
    if missing and not args.allow_partial:
        errors.append(f"missing {len(missing)} task ids: {sorted(missing)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    coverage = len(seen & expected_ids)
    print(f"OK: {len(rows)} unique rows; benchmark coverage {coverage}/{len(expected_ids)}")


if __name__ == "__main__":
    main()

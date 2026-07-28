#!/usr/bin/env python3
"""Build the exact per-task InMind long-horizon conversation timeline."""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS = ROOT / "benchmark" / "dataset" / "inmind.jsonl"
DEFAULT_BACKGROUND = ROOT / "evaluation" / "background" / "lme_s_background.jsonl"
DEFAULT_MANIFEST = ROOT / "evaluation" / "background" / "manifest.json"


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
            rows.append(row)
    return rows


def session_id(turn_id: str) -> str:
    if "-turn-" not in turn_id:
        raise ValueError(f"Background turn id has no '-turn-' suffix: {turn_id}")
    return turn_id.rsplit("-turn-", 1)[0]


def group_sessions(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    closed: set[str] = set()
    previous: str | None = None

    for turn in turns:
        turn_id = str(turn.get("id", ""))
        sid = session_id(turn_id)
        if sid != previous:
            if sid in closed:
                raise ValueError(f"Session {sid} is not contiguous in the background file")
            if previous is not None:
                closed.add(previous)
            previous = sid
        copied = dict(turn)
        copied["source"] = "lme_s_background"
        grouped.setdefault(sid, []).append(copied)

    return [{"session_id": sid, "turns": rows} for sid, rows in grouped.items()]


def select_task(tasks: list[dict[str, Any]], task_id: int) -> dict[str, Any]:
    matches = [task for task in tasks if int(task.get("task_id", -1)) == task_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one task_id={task_id}, found {len(matches)}")
    return matches[0]


def build_timeline(
    task: dict[str, Any],
    background_turns: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    sessions = group_sessions(background_turns)
    injection_index = int(manifest["injection_session_index"])
    if not 0 <= injection_index < len(sessions):
        raise ValueError(f"Invalid injection_session_index={injection_index}")

    task_id = int(task["task_id"])
    target_turns = [
        {
            "id": f"inmind-task-{task_id}-turn-0",
            "role": "user",
            "content": task["user_message"],
            "source": "inmind_target",
        },
        {
            "id": f"inmind-task-{task_id}-turn-1",
            "role": "assistant",
            "content": task["assistant_message"],
            "source": "inmind_target",
        },
    ]
    sessions[injection_index]["turns"].extend(target_turns)

    return {
        "task_id": task_id,
        "protocol": {
            "name": "inmind-middle-injection-v1",
            "background_sessions": len(sessions),
            "background_turns": len(background_turns),
            "injection_session_index": injection_index,
            "injection_session_number": injection_index + 1,
            "phase_a_sessions": injection_index,
            "prefix_user_turns": int(manifest["prefix_user_turns"]),
            "injection_user_turn_locator": int(manifest["injection_user_turn_locator"]),
            "background_user_turns_before_target": int(
                manifest["background_user_turns_before_target"]
            ),
            "post_injection_sessions": len(sessions) - injection_index - 1,
            "target_position": "end_of_injection_session",
            "query_state_policy": "naive and indirect queries read the same frozen post-history state",
        },
        "sessions": sessions,
        "queries": {
            "naive_query": task["naive_query"],
            "query": task["query"],
        },
    }


def write_json(value: dict[str, Any], output: Path | None, compact: bool) -> None:
    text = json.dumps(
        value,
        ensure_ascii=False,
        indent=None if compact else 2,
        separators=(",", ":") if compact else None,
    ) + "\n"
    if output is None:
        sys.stdout.write(text)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append one InMind target turn to the ninth session of the fixed LME-s trace."
    )
    parser.add_argument("--task-id", type=int, required=True)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--background", type=Path, default=DEFAULT_BACKGROUND)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    task = select_task(read_jsonl(args.tasks), args.task_id)
    background = read_jsonl(args.background)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    write_json(build_timeline(task, background, manifest), args.output, args.compact)


if __name__ == "__main__":
    main()

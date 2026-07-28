#!/usr/bin/env python3
"""Validate the public InMind task, background, prompt, and protocol artifacts."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    task_path = ROOT / "benchmark" / "dataset" / "inmind.jsonl"
    background_path = ROOT / "evaluation" / "background" / "lme_s_background.jsonl"
    manifest_path = ROOT / "evaluation" / "background" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tasks = read_jsonl(task_path)
    turns = read_jsonl(background_path)

    assert len(tasks) == 125, f"expected 125 tasks, found {len(tasks)}"
    task_ids = [int(task["task_id"]) for task in tasks]
    assert len(set(task_ids)) == len(task_ids), "duplicate task_id"

    roles = Counter(turn["role"] for turn in turns)
    session_ids = [turn["id"].rsplit("-turn-", 1)[0] for turn in turns]
    ordered_sessions = list(dict.fromkeys(session_ids))
    assert len(turns) == manifest["turns"] == 486
    assert len(ordered_sessions) == manifest["sessions"] == 47
    assert roles["user"] == manifest["user_turns"] == 240
    assert roles["assistant"] == manifest["assistant_turns"] == 246

    digest = hashlib.sha256(background_path.read_bytes()).hexdigest()
    assert digest == manifest["sha256"], "background SHA-256 mismatch"

    injection_index = int(manifest["injection_session_index"])
    assert injection_index == 8
    assert len(ordered_sessions) - injection_index - 1 == manifest["post_injection_sessions"] == 38
    prefix_sessions = set(ordered_sessions[:injection_index])
    prefix_user_turns = sum(
        turn["role"] == "user" and sid in prefix_sessions
        for turn, sid in zip(turns, session_ids)
    )
    assert prefix_user_turns == manifest["prefix_user_turns"] == 35
    injection_sessions = set(ordered_sessions[: injection_index + 1])
    through_injection_user_turns = sum(
        turn["role"] == "user" and sid in injection_sessions
        for turn, sid in zip(turns, session_ids)
    )
    assert (
        through_injection_user_turns
        == manifest["background_user_turns_before_target"]
        == 41
    )
    assert prefix_user_turns < manifest["injection_user_turn_locator"] <= through_injection_user_turns

    prompt_expectations = {
        "answer_system.txt": ["{context}", "proactively mention"],
        "judge_naive.txt": ["context", "answer", "\"score\""],
        "judge_application.txt": ["context_recall", "answer_warning", "\"score\""],
        "judge_target_recall.txt": ["Do NOT judge any answer", "\"score\""],
        "judge_answer_only.txt": ["Do NOT decide whether any retrieved context", "\"score\""],
    }
    for name, needles in prompt_expectations.items():
        text = (ROOT / "evaluation" / "prompts" / name).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"{name} missing {needle!r}"

    schema = json.loads(
        (ROOT / "evaluation" / "schema" / "submission.schema.json").read_text(encoding="utf-8")
    )
    assert schema["required"] == ["task_id", "system", "config", "naive", "query"]

    print(
        "OK: 125 tasks; 47 sessions; 486 turns; injection session 9; "
        "40th-user-turn locator verified; target follows 41 background user turns; "
        "38 post-injection sessions; "
        "background SHA-256 verified"
    )


if __name__ == "__main__":
    main()

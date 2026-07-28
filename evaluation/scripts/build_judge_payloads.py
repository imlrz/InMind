#!/usr/bin/env python3
"""Build judge requests from an InMind system-output JSONL file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASKS = ROOT / "benchmark" / "dataset" / "inmind.jsonl"
PROMPT_DIR = ROOT / "evaluation" / "prompts"
PROMPTS = {
    "naive": PROMPT_DIR / "judge_naive.txt",
    "application": PROMPT_DIR / "judge_application.txt",
    "target-recall": PROMPT_DIR / "judge_target_recall.txt",
    "answer-only": PROMPT_DIR / "judge_answer_only.txt",
}


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


def user_payload(metric: str, task: dict[str, Any], result: dict[str, Any]) -> str:
    if metric == "naive":
        return (
            f"user_message: {task['user_message']}\n"
            f"context: {result['naive']['context']}\n"
            f"query: {task['naive_query']}\n"
            f"answer: {result['naive']['answer']}"
        )
    if metric == "target-recall":
        return (
            f"user_message: {task['user_message']}\n"
            f"context: {result['query']['context']}\n"
            f"query: {task['query']}\n"
            f"explanation: {task['explanation']}"
        )
    if metric == "application":
        return (
            f"user_message: {task['user_message']}\n"
            f"context: {result['query']['context']}\n"
            f"query: {task['query']}\n"
            f"explanation: {task['explanation']}\n"
            f"answer: {result['query']['answer']}"
        )
    if metric == "answer-only":
        return (
            f"user_message: {task['user_message']}\n"
            f"query: {task['query']}\n"
            f"explanation: {task['explanation']}\n"
            f"answer: {result['query']['answer']}"
        )
    raise ValueError(metric)


def build_rows(
    metric: str,
    tasks: dict[int, dict[str, Any]],
    results: Iterable[dict[str, Any]],
) -> Iterable[dict[str, Any]]:
    system_prompt = PROMPTS[metric].read_text(encoding="utf-8").rstrip()
    for result in results:
        task_id = int(result["task_id"])
        if task_id not in tasks:
            raise ValueError(f"Unknown task_id={task_id}")
        task = tasks[task_id]
        yield {
            "task_id": task_id,
            "metric": metric,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_payload(metric, task, result)},
            ],
            "response_contract": {"score": "0 or 1", "reason": "brief explanation"},
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--metric", choices=sorted(PROMPTS), required=True)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    tasks = {int(task["task_id"]): task for task in read_jsonl(args.tasks)}
    rows = build_rows(args.metric, tasks, read_jsonl(args.results))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
    output = args.output.open("w", encoding="utf-8") if args.output else sys.stdout
    try:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
    finally:
        if args.output:
            output.close()


if __name__ == "__main__":
    main()

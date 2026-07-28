---
name: evaluate-inmind
description: Evaluate long-term memory systems on the InMind benchmark using the fixed LME-s background, canonical middle injection, shared answer prompt, and binary judges. Use when an agent needs to integrate a memory method, run InMind tasks, construct per-task timelines, validate result JSONL, build judge requests, compare metrics, or prepare a leaderboard submission.
---

# Evaluate on InMind

Run a memory system against the public InMind protocol without leaking judge-only fields or changing the long-horizon timeline.

## Locate and validate the benchmark

1. Locate the repository root by finding `benchmark/dataset/inmind.jsonl` and `evaluation/README.md`.
2. Read `evaluation/README.md` before implementing an adapter.
3. Read `references/protocol.md` for the non-negotiable agent contract.
4. Run:

```bash
python evaluation/scripts/validate_release.py
```

Stop and report the mismatch if validation fails. Do not silently repair, reorder, filter, or regenerate benchmark artifacts.

## Choose the integration path

- Use the **stateful path** for memory systems that ingest conversations over time. Replay the 47 sessions in order and inject the target pair at the canonical middle position.
- Use the **single-shot control path** only for stateless retrieval baselines. Index the 486 background turns and one task-local target chunk, and label the run as a single-shot retrieval control.

Do not report a tail-injection or altered-background run as protocol-comparable.

## Build and replay each task

Generate the exact task timeline:

```bash
python evaluation/scripts/build_timeline.py \
  --task-id <TASK_ID> \
  --output /tmp/inmind-task-<TASK_ID>.json
```

For a stateful method:

1. Start from empty task-specific state or copy an immutable prefix state built from the first eight sessions.
2. Process each session through the method's normal update path.
3. Preserve turn order and roles.
4. Freeze the state after all 47 sessions.
5. Run the direct `naive_query` and indirect `query` independently from that same frozen state.
6. Prevent both test queries and answers from being written back before both evaluations finish.

Never expose `explanation`, `entity_1`, `entity_2`, `relation`, or `provenance` to the system under test.

## Generate answers

Use `gpt-5-mini` for a leaderboard-comparable run. Apply `evaluation/prompts/answer_system.txt`, replacing `{context}` with the exact text visible to the answer model.

Capture:

- the exact context shown for each query;
- the generated answer;
- method name and full configuration;
- model, embedding, retrieval depth, and relevant seeds or versions.

Write one row per task using `evaluation/schema/submission.schema.json`.

## Validate and judge

Validate coverage and structure:

```bash
python evaluation/scripts/validate_submission.py results.jsonl
```

Build judge messages:

```bash
python evaluation/scripts/build_judge_payloads.py \
  --results results.jsonl \
  --metric <naive|target-recall|application|answer-only> \
  --output judge-requests.jsonl
```

Use `gpt-5-mini` with a 4,096-token output limit and no temperature or top-p override for paper-comparable judging. Parse only JSON verdicts with binary `score`.

Report these primary metrics over all 125 tasks:

- Naive recall
- Target recall
- Application

Treat answer-only as a diagnostic, not a replacement for context-aware Application.

## Audit before reporting

Confirm:

- all 125 task IDs occur exactly once;
- each task used an isolated target-dependent state;
- the target was appended to the end of session 9;
- 38 complete sessions followed the target;
- naive and indirect evaluation read the same frozen state;
- stored `context` exactly matches what the answer model saw;
- judge-only fields were withheld until evaluation;
- raw outputs and configuration are retained.

Do not claim team verification. For leaderboard consideration, package the configuration, per-task contexts and answers, judge verdicts, and reproducible commands, then contact `imlrz@mail.ustc.edu.cn`.

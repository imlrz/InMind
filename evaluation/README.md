# Evaluation package

This package contains the fixed long-horizon background, target-injection helper, answer prompt, judge prompts, and submission contract needed to test a memory system on InMind.

## Contents

| Path | Purpose |
| --- | --- |
| `background/lme_s_background.jsonl` | Fixed 47-session, 486-turn LME-s background trace |
| `background/manifest.json` | Provenance, integrity hash, counts, and injection constants |
| `prompts/answer_system.txt` | Shared answer-system prompt used in the paper |
| `prompts/judge_naive.txt` | Context-aware direct-recall judge |
| `prompts/judge_target_recall.txt` | Answer-blind target-recall judge |
| `prompts/judge_application.txt` | Context-aware end-to-end application judge |
| `prompts/judge_answer_only.txt` | Optional answer-only diagnostic judge |
| `schema/submission.schema.json` | Per-task result contract |
| `examples/submission.example.jsonl` | Minimal partial result example |
| `scripts/build_timeline.py` | Build one task's exact 47-session injected timeline |
| `scripts/validate_submission.py` | Check result structure, task IDs, and coverage |
| `scripts/build_judge_payloads.py` | Materialize judge messages without making API calls |
| `scripts/validate_release.py` | Verify benchmark and background integrity |

All scripts use only the Python standard library.

## Standard protocol

Evaluate every task independently. A task's target memory is the two-message pair:

```text
User: {user_message}
Assistant: {assistant_message}
```

For a stateful memory system:

1. Start from an empty per-task memory state.
2. Process the first eight background sessions in order.
3. Take the ninth session, which is the first session whose cumulative background user-turn count reaches 40.
4. Append the target user/assistant pair to the **end** of that ninth session.
5. Process the complete ninth session.
6. Process the remaining 38 sessions in their original order.
7. Freeze or snapshot the resulting state.
8. Evaluate `naive_query` and `query` independently from that same frozen state.

The target is therefore followed by 38 full sessions of ordinary interaction before either test query is issued. Every task uses the same background and insertion point; only the target pair changes.

The paper configuration names the locator `inject-turn 40`: it selects the session containing the 40th background user turn. Session boundaries are preserved, so the complete ninth session is processed and the target is appended after its sixth user turn. Consequently, 41 background user turns—not a truncated 40-turn prefix—precede the target. Use the session boundary rather than splitting session 9.

Do not:

- inject the target after all background turns;
- move the target to its own later session;
- expose `entity_1`, `entity_2`, `relation`, `explanation`, or `provenance` to the system under test;
- let the naive query, its retrieval, or its answer alter the state used by the indirect query;
- reuse target-dependent state between different tasks.

A shared immutable prefix bank built from the first eight sessions is allowed. Copy it into a separate task state before processing the injection session and remaining sessions.

### Build a task timeline

```bash
python evaluation/scripts/build_timeline.py \
  --task-id 155 \
  --output /tmp/inmind-task-155.json
```

The output groups the background into 47 ordered sessions and appends two `source: "inmind_target"` turns to session index `8` (the ninth session). It also includes the two test queries outside the timeline.

Replay each session through the memory system's normal update path. Do not ingest the `queries` object into memory.

### Single-shot retrieval controls

A stateless Naive RAG control cannot model online session updates. For that control only, use the 486 background turns as individual chunks and add the target user/assistant pair as one task-local 487th chunk. Retrieve independently for the naive and indirect queries. Report this explicitly as a single-shot retrieval control rather than a stateful middle-injection run.

## Answer generation

For leaderboard-comparable runs, use `gpt-5-mini` as the shared answer backbone with a maximum of 16,384 output tokens and no temperature or top-p override.

The answer model receives:

```json
[
  {
    "role": "system",
    "content": "evaluation/prompts/answer_system.txt with {context} replaced by the exact system context"
  },
  {
    "role": "user",
    "content": "the naive_query or query"
  }
]
```

`context` must be the exact textual context made visible to the answer model after the memory system retrieves, routes, summarizes, or otherwise selects memory. Preserve it in the output record for judging and audit.

If a method maintains always-visible state, include that visible state in `context`. Do not include hidden storage that the answer model could not access.

## Result format

Write one JSON object per task:

```json
{
  "task_id": 155,
  "system": "ExampleMemory",
  "config": {
    "embedding": "example-embedding",
    "retrieval_top_k": 10,
    "answer_model": "gpt-5-mini"
  },
  "naive": {
    "context": "the exact context shown for the direct query",
    "answer": "the generated direct-query answer"
  },
  "query": {
    "context": "the exact context shown for the indirect query",
    "answer": "the generated indirect-query answer"
  }
}
```

Validate a full submission:

```bash
python evaluation/scripts/validate_submission.py results.jsonl
```

Use `--allow-partial` only for development runs. Leaderboard submissions require all 125 task IDs.

A one-task placeholder illustrating the contract is available at `examples/submission.example.jsonl`:

```bash
python evaluation/scripts/validate_submission.py \
  evaluation/examples/submission.example.jsonl \
  --allow-partial
```

## Judging

The paper uses `gpt-5-mini` as the binary judge with a maximum of 4,096 output tokens and no temperature or top-p override. A judge response must be:

```json
{"score": 0, "reason": "brief explanation"}
```

Build exact judge request messages without sending them:

```bash
python evaluation/scripts/build_judge_payloads.py \
  --results results.jsonl \
  --metric target-recall \
  --output target-recall-requests.jsonl
```

Supported metrics:

| Metric | Judge inputs | Meaning |
| --- | --- | --- |
| `naive` | target fact, direct-query context, direct query, answer | Fact was available and correctly recalled |
| `target-recall` | target fact, indirect-query context, indirect query, explanation | Target fact reached the answerer's context |
| `application` | target fact, indirect-query context, indirect query, explanation, answer | End-to-end context-aware application |
| `answer-only` | target fact, indirect query, explanation, answer | Optional behavior diagnostic without retrieval attribution |

Higher is better. Aggregate each primary metric as the number of `score: 1` verdicts divided by 125. Keep raw contexts, answers, judge responses, model names, and method configuration for audit.

The `explanation` field is judge-only ground truth. Never expose it to the memory system, retriever, query planner, or answer model.

## Integrity and provenance

Run:

```bash
python evaluation/scripts/validate_release.py
```

The fixed background is derived from LongMemEval-s and distributed with upstream attribution and its MIT license under `background/`. The InMind task checksum remains in `benchmark/dataset/SHA256SUMS`.

For leaderboard consideration, email the complete configuration and reproducible result package to `imlrz@mail.ustc.edu.cn`.

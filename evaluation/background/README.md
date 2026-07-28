# Fixed LME-s background

`lme_s_background.jsonl` is the fixed 47-session, 486-turn background conversation used for every InMind task in the paper.

The trace comes from the cleaned LongMemEval-s instance `0bc8ad93` in [`xiaowu0162/LongMemEval`](https://github.com/xiaowu0162/LongMemEval). It is redistributed under the upstream MIT license in `LICENSE.LongMemEval`. The source paper is [LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory](https://arxiv.org/abs/2410.10813).

Each JSONL row is one original background turn:

```json
{
  "id": "session-...-turn-0",
  "role": "user",
  "content": "...",
  "timestamp_mapping": {"question:0bc8ad93": "..."}
}
```

Rows are ordered chronologically. A session ID is the portion of `id` before `-turn-`. Do not shuffle, deduplicate, summarize, or remove turns before passing them to the system under test unless that transformation is the memory method being evaluated.

The exact file hash and injection constants are recorded in `manifest.json`.

The paper's `inject-turn 40` setting locates the session containing the 40th user turn. That is session 9. The target pair is appended only after the complete session, so 41 original background user turns precede the target; session 9 must not be split.

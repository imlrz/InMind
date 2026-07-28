# InMind agent contract

## Canonical artifacts

- Tasks: `benchmark/dataset/inmind.jsonl`
- Background: `evaluation/background/lme_s_background.jsonl`
- Background constants: `evaluation/background/manifest.json`
- Answer prompt: `evaluation/prompts/answer_system.txt`
- Judge prompts: `evaluation/prompts/judge_*.txt`
- Result contract: `evaluation/schema/submission.schema.json`

## Timeline

Use 47 ordered LME-s sessions containing 486 original turns. Process sessions 1–8 first (35 user turns). The paper's `inject-turn 40` setting locates session 9 because it contains the 40th user turn. Preserve the full session: it has six user turns, so append the task's `user_message` and `assistant_message` after 41 cumulative background user turns. Then process sessions 10–47. This leaves 38 sessions after the target.

The injection-session index is zero-based `8`. Do not interpret it as raw turn index 8.

## Isolation

Create independent target-dependent state per task. A shared state is permitted only for the immutable prefix formed from sessions 1–8. Fork or copy it before injecting a target.

Evaluate `naive_query` and `query` from the identical frozen state after session 47. Retrieval may differ by query, but one test turn must not mutate the other's state.

## Leakage boundary

Allow the system under test to see only:

- background session turns;
- the target `user_message` and `assistant_message` at injection time;
- one test query at answer time.

Reserve `explanation`, entities, relation, provenance, and judge prompts for post-hoc evaluation.

## Context boundary

Record only information actually visible to the answer model as `context`. Include retrieved memory, summaries, profiles, routed state, or other visible memory. Exclude hidden database contents and internal state that was not placed in the answer call.

## Comparable answer and judge calls

- Answer backbone: `gpt-5-mini`
- Answer maximum output: 16,384 tokens
- Judge: `gpt-5-mini`
- Judge maximum output: 4,096 tokens
- Temperature/top-p: provider defaults, with no override

Record deviations and do not present them as an exact reproduction.

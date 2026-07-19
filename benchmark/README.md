# InMind benchmark

## Research question

InMind asks whether an agent can use a remembered personal fact when the relevance of that fact is created by world knowledge rather than by surface similarity to the current query.

Let `m` be a personal memory, `q` a later query, and `k` a knowledge bridge. An InMind task is designed so that:

1. `m` changes what a safe, correct, or appropriately personalized answer to `q` should say;
2. `m` and `q` do not provide an obvious lexical or topical retrieval cue; and
3. background knowledge `k` connects the two.

The benchmark therefore targets knowledge-mediated application of explicit user facts, not merely direct factual recall.

## Task structure

Every task contains:

| Field | Role |
| --- | --- |
| `user_message` | The personal fact introduced into memory |
| `assistant_message` | A short acknowledgement paired with the memory turn |
| `naive_query` | A direct query that tests whether the fact is retrievable on demand |
| `query` | An indirect query whose answer should change because of the fact |
| `explanation` | The expected application and knowledge bridge used for evaluation |
| `entity_1`, `entity_2`, `relation` | Optional structured representation of the bridge |

The structured bridge fields are absent for some tasks retained from the original 90-task set; `explanation` is present for all 125 tasks.

## Evaluation axes

The full evaluation release will separate three measurements:

- **Naive recall:** whether the system can answer the direct recall query.
- **Target recall:** whether the decisive personal fact is present in the context supplied for the indirect query. This measurement is answer-blind.
- **Application:** whether the final answer actually applies the expected knowledge bridge.

Keeping these measurements separate helps distinguish storage failure, retrieval failure, and answer-generation failure.

## Dataset composition

The current release contains 125 tasks across ten life domains:

| Domain | Count | Share |
| --- | ---: | ---: |
| `consumer` | 5 | 4.0% |
| `financial` | 8 | 6.4% |
| `health_and_wellness` | 46 | 36.8% |
| `legal` | 7 | 5.6% |
| `other` | 3 | 2.4% |
| `parenting` | 4 | 3.2% |
| `personal_development` | 3 | 2.4% |
| `professional_and_career` | 26 | 20.8% |
| `relationships` | 16 | 12.8% |
| `spirituality` | 7 | 5.6% |

The public `task_id` values are sparse and stable. They preserve the identifiers used by the paper and its experiment records; for example, the tree-nut-allergy/macaron example is Task 155. Consumers must not assume IDs are contiguous or use the ID as a zero-based row index.

## Release derivation

This 125-task release corresponds to the internally audited `final-v6a` build. It was derived from a larger candidate set after annotation, similarity filtering, and removal of four hard-conflict tasks. Internal file paths, API usage records, and model-service metadata have been removed from the public dataset.

## Intended use

InMind is intended for:

- evaluating long-term-memory retrieval and routing;
- comparing direct recall with knowledge-mediated application;
- diagnosing whether a failure occurred before or after the answer model received the relevant fact; and
- studying hybrid retrieval and always-visible memory designs.

It is not intended as a knowledge base, a source of professional advice, or a benchmark of general medical/legal correctness independent of its documented task expectations.

## Limitations

- The benchmark has 125 tasks, so small percentage differences should not be over-interpreted.
- Health, wellness, and safety scenarios are intentionally prominent.
- Some bridges are jurisdiction- or context-dependent in real deployments even when the benchmark expectation is binary.
- The current public provenance metadata is incomplete for tasks retained from the original 90-task set and for human-curated tasks.
- A system optimized only for positive reminders could over-warn; this release does not yet include matched negative controls.

See [dataset/README.md](dataset/README.md) for file formats and provenance coverage.

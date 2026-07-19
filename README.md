# InMind

**Keep It InMind: Benchmarking the Implicit-Association Blind Spot in Agent Memory**

InMind is a 125-task benchmark for testing whether a long-term-memory agent can apply a previously stated user fact when the later query is only connected to that fact through world knowledge.

This is the initial, data-only repository release. It contains the benchmark definition and English dataset. Evaluation code, baseline adapters, paper results, and archival artifacts will be added in later stages.

## Motivation

Retrieval-based memory works naturally when a query resembles the memory it needs. InMind targets a different case: the memory and query can be semantically distant even though the memory is decision-critical.

For example:

- Earlier memory: the user reports a tree-nut allergy.
- Direct recall query: “What food allergy did I tell you about?”
- Indirect application query: “I want to try making macarons this weekend. Any good recipes?”
- Knowledge bridge: macarons are commonly made with almond flour.

The direct query tests whether the fact can be recalled on demand. The indirect query tests whether the agent surfaces and applies that fact when the user does not provide an obvious retrieval cue.

## Benchmark at a glance

| Property | Value |
| --- | --- |
| Tasks | 125 |
| Evaluation language | English |
| Domains | 10 |
| User facts | Synthetic |
| Task structure | Memory turn + direct recall query + indirect application query |
| Stable IDs | Sparse integer `task_id` values retained from the audited benchmark |

Domain distribution:

| Domain | Tasks |
| --- | ---: |
| Consumer | 5 |
| Financial | 8 |
| Health and wellness | 46 |
| Legal | 7 |
| Other | 3 |
| Parenting | 4 |
| Personal development | 3 |
| Professional and career | 26 |
| Relationships | 16 |
| Spirituality | 7 |

## Repository contents

```text
benchmark/
├── README.md
└── dataset/
    ├── README.md
    ├── inmind.jsonl
    ├── schema.json
    └── SHA256SUMS
```

- [Benchmark documentation](benchmark/README.md)
- [Dataset card and field definitions](benchmark/dataset/README.md)
- [English dataset](benchmark/dataset/inmind.jsonl)

## Quick inspection

The dataset is JSON Lines, with one task per line.

```bash
wc -l benchmark/dataset/inmind.jsonl
jq 'select(.task_id == 155)' benchmark/dataset/inmind.jsonl
```

The first command should report 125 records. Task IDs are intentionally not renumbered because the paper and experiment records refer to the retained IDs directly.

## Data statement

All user facts and conversations in InMind are synthetic. Some tasks describe medical conditions, immigration status, religious practice, financial circumstances, intimate-partner violence, or other sensitive situations because these are settings where failure to apply remembered information can be consequential. The benchmark is an evaluation artifact, not medical, legal, or financial advice.

Knowledge-source metadata is included where it was available in the audited build. See the [dataset documentation](benchmark/dataset/README.md#provenance-coverage) for current coverage and limitations.

## Release status

- [x] Benchmark definition
- [x] English dataset
- [ ] Evaluation package and judge prompts
- [ ] Baseline adapters and pinned dependency versions
- [ ] Paper-aligned aggregate and per-task results
- [ ] Citation metadata and archival release

License and citation metadata will be added before the formal archival release.

# Dataset card

## Files

| File | Records | Description |
| --- | ---: | --- |
| `inmind_en.jsonl` | 125 | Flat English evaluation records |
| `inmind_bilingual.jsonl` | 125 | Canonical English–Chinese records with shared metadata |
| `schema_en.json` | — | JSON Schema for one English JSONL record |
| `schema_bilingual.json` | — | JSON Schema for one bilingual JSONL record |
| `SHA256SUMS` | — | Checksums for the two dataset files |

Both JSONL files are ordered by `task_id` and describe the same 125 tasks.

## English record

```json
{
  "task_id": 155,
  "domain": "health_and_wellness",
  "entity_1": null,
  "entity_2": null,
  "relation": null,
  "explanation": "Macarons are made with almond flour...",
  "user_message": "Just found out I have a tree nut allergy...",
  "assistant_message": "Tree nut allergies can be quite severe...",
  "naive_query": "What food allergy did I tell you about?",
  "query": "I want to try making macarons this weekend. Any good recipes?",
  "provenance": {
    "source_dataset": "task-v1-90",
    "source_task_id": 1,
    "original_task_id": 1
  }
}
```

## Field definitions

| Field | Type | Description |
| --- | --- | --- |
| `task_id` | integer | Stable, sparse task identifier used by the paper |
| `domain` | string | One of the ten benchmark domains |
| `entity_1` | string or null | First entity in the structured bridge |
| `entity_2` | string or null | Second entity in the structured bridge |
| `relation` | string or null | Relation connecting the entities |
| `explanation` | string | Expected application and knowledge bridge |
| `user_message` | string | Personal fact introduced into memory |
| `assistant_message` | string | Acknowledgement paired with the memory turn |
| `naive_query` | string | Direct recall query |
| `query` | string | Indirect application query |
| `provenance` | object | Build origin and optional knowledge-source trace |

The bilingual file moves all language-dependent fields under `en` and `zh`. Shared fields (`task_id`, `domain`, and `provenance`) remain at the top level.

## Stable identifiers

Task IDs are not contiguous: the release retains 125 IDs between 0 and 225. Do not rewrite them as row numbers. Use `task_id` for joins with future per-task results.

## Provenance coverage

The public release removes local filesystem paths, raw generation usage, service credentials, and internal annotation timestamps. The remaining `provenance.knowledge_source` object may contain a source URL and source/chunk identifiers.

Current coverage:

| Provenance category | Tasks |
| --- | ---: |
| Attached source URL | 77 |
| Human-expert task with no attached URL | 12 |
| Task retained from the original 90-task set with no attached knowledge-source record | 36 |

Missing source metadata is represented by the absence of `knowledge_source`; it must not be interpreted as evidence that no external bridge exists. Completing and independently checking these traces is part of the archival-release roadmap.

## Loading the data

Python:

```python
import json
from pathlib import Path

path = Path("benchmark/dataset/inmind_en.jsonl")
tasks = [json.loads(line) for line in path.read_text().splitlines() if line]
by_id = {task["task_id"]: task for task in tasks}

assert len(tasks) == 125
print(by_id[155]["query"])
```

Command line:

```bash
jq -c 'select(.domain == "legal")' benchmark/dataset/inmind_en.jsonl
sha256sum -c benchmark/dataset/SHA256SUMS
```

On macOS, use `shasum -a 256` to recompute hashes if `sha256sum` is unavailable.

## Data and safety

All personal facts and dialogues are synthetic. The benchmark includes sensitive scenarios solely to evaluate whether an agent applies remembered constraints. Dataset text should not be presented to users as professional advice.

License information will be added before the formal archival release.

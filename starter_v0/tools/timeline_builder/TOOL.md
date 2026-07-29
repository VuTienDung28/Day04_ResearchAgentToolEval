---
name: timeline_builder
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [items, order]
outputs: [status, items, undated_items, dated_count, undated_count, message]
side_effect: false
---
# timeline_builder

Sorts already-collected research items into a chronological timeline.

Use it only when dated items are supplied and the user asks to organize events
chronologically. Do not confuse it with `timeline`, which retrieves recent
posts from one social account. This tool does not search or fetch data.

Arguments:

- `items` (required): list of objects using `date`, `published_at`, or
  `updated_at`.
- `order` (optional): `ascending` (default) or `descending`.

The result contains dated `items`, separate `undated_items`, counts, status,
and message. It requires no environment variables, has no side effects, and
requires no confirmation.

Direct smoke test from `starter_v0/`:

```powershell
python -c "import json; from tools.timeline_builder.tool import build_timeline; r=build_timeline([{'title':'Second','date':'2026-02-01'},{'title':'First','date':'2026-01-01'},{'title':'Unknown'}]); json.dumps(r); assert r['status']=='ok' and r['items'][0]['title']=='First' and r['undated_count']==1; print(r)"
```

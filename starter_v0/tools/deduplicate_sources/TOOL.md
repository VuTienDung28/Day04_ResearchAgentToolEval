---
name: deduplicate_sources
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [items, match_by]
outputs: [status, items, removed_count, message]
side_effect: false
---
# deduplicate_sources

Removes duplicate research sources using normalized URLs or titles.

Use it after source items have already been collected and the user asks to
remove duplicates. Do not use it to search, fetch, summarize, rank, or verify
sources.

Arguments:

- `items` (required): list of JSON-serializable source objects.
- `match_by` (optional): `url`, `title`, or `url_or_title` (default).

The tool returns `status`, deduplicated `items`, `removed_count`, and `message`.
It requires no environment variables, has no side effects, and requires no
confirmation.

Safe invocation and direct smoke test from `starter_v0/`:

```powershell
python -c "import json; from tools.deduplicate_sources.tool import deduplicate_sources; r=deduplicate_sources([{'title':'AI News','url':'https://example.com/a'},{'title':'AI News','url':'https://example.com/a?utm_source=rss'},{'title':'Robotics','url':'https://example.com/b'}]); json.dumps(r); assert r['status']=='ok' and r['removed_count']==1 and len(r['items'])==2; print(r)"
```

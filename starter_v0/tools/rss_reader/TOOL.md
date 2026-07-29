---
name: rss_reader
track: bonus
kind: live_api
provider: RSS/Atom
requires_env: []
inputs: [feed_url, limit]
outputs: [status, items, message]
side_effect: false
---
# rss_reader

Reads recent entries from a public RSS or Atom feed URL.

Use it only when the user supplies or explicitly requests reading a known feed.
Do not use it for a normal article URL, broad web search, social search, or
page extraction; use `fetch` for a single normal page.

Arguments:

- `feed_url` (required): absolute `http` or `https` RSS/Atom feed URL.
- `limit` (optional): number of entries, from 1 to 50; default 5.

The tool returns `status`, `items`, and `message`. Each item contains `title`,
`url`, `summary`, `published_at`, and `source` where available. It needs
internet access but no API key, has no side effects, and requires no
confirmation.

Direct validation smoke test from `starter_v0/`:

```powershell
python -c "import json; from tools.rss_reader.tool import read_rss_feed; r=read_rss_feed('not-a-url'); json.dumps(r); assert r['status']=='error' and r['items']==[]; print(r)"
```

For a live smoke test, replace the URL with a public RSS/Atom feed and assert
`status == "ok"`. A validation-only test does not prove the live feed is
reachable.

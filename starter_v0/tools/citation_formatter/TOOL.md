---
name: citation_formatter
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [items, style]
outputs: [status, text, citation_count, message]
side_effect: false
---
# citation_formatter

Formats supplied source metadata as a citation list.

Use it when source items already exist and the user explicitly requests
citations or a bibliography. Do not use it to search, fetch, summarize, verify,
or create missing bibliographic facts. The `apa` option is a compact APA-like
format, not a full style-guide validator.

Arguments:

- `items` (required): source objects with available fields such as `title`,
  `url`, `authors`/`author`, `source`, and `year`/`published_at`.
- `style` (optional): `markdown` (default), `numbered`, or `apa`.

The tool returns `status`, `text`, `citation_count`, and `message`. It requires
no environment variables, has no side effects, and requires no confirmation.

Direct smoke test from `starter_v0/`:

```powershell
python -c "import json; from tools.citation_formatter.tool import format_citations; r=format_citations([{'title':'Attention Is All You Need','url':'https://arxiv.org/abs/1706.03762','authors':['Ashish Vaswani'],'year':'2017'}]); json.dumps(r); assert r['status']=='ok' and r['citation_count']==1 and 'Attention Is All You Need' in r['text']; print(r)"
```

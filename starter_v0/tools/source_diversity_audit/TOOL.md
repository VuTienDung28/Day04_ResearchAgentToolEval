---
name: source_diversity_audit
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [items, concentration_threshold]
outputs: [status, source_count, unique_domain_count, domain_distribution, dominant_domain, dominant_share, unknown_domain_count, is_concentrated, message]
side_effect: false
---
# source_diversity_audit

Measures how a supplied source list is distributed across domains.

Use it when source items already exist and the user asks about source diversity
or domain concentration. Do not use it to search, fact-check, rank credibility,
or claim that a source is trustworthy.

Arguments:

- `items` (required): list of source objects containing URLs.
- `concentration_threshold` (optional): number from 0 to 1; default 0.5.

The tool returns domain counts and a transparent concentration calculation. It
requires no environment variables, has no side effects, and requires no
confirmation.

Direct smoke test from `starter_v0/`:

```powershell
python -c "import json; from tools.source_diversity_audit.tool import audit_source_diversity; r=audit_source_diversity([{'url':'https://a.com/1'},{'url':'https://a.com/2'},{'url':'https://b.org/3'}]); json.dumps(r); assert r['status']=='ok' and r['unique_domain_count']==2 and r['dominant_domain']=='a.com'; print(r)"
```

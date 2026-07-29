from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlsplit


def _error(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "source_count": 0,
        "unique_domain_count": 0,
        "domain_distribution": {},
        "dominant_domain": None,
        "dominant_share": 0.0,
        "unknown_domain_count": 0,
        "is_concentrated": False,
        "message": message,
    }


def _domain(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    try:
        hostname = (urlsplit(value.strip()).hostname or "").lower()
    except ValueError:
        return ""
    return hostname[4:] if hostname.startswith("www.") else hostname


def audit_source_diversity(
    items: list[dict[str, Any]],
    concentration_threshold: float = 0.5,
) -> dict[str, Any]:
    """Measure domain concentration without judging source truthfulness."""
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        return _error("items must be a list of objects")
    if isinstance(concentration_threshold, bool) or not isinstance(concentration_threshold, (int, float)):
        return _error("concentration_threshold must be a number between 0 and 1")
    threshold = float(concentration_threshold)
    if not 0 <= threshold <= 1:
        return _error("concentration_threshold must be a number between 0 and 1")

    domains = [_domain(item.get("url")) for item in items]
    known_domains = [value for value in domains if value]
    counts = Counter(known_domains)
    ordered_counts = dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])))
    dominant_domain = next(iter(ordered_counts), None)
    dominant_count = ordered_counts.get(dominant_domain, 0) if dominant_domain else 0
    dominant_share = round(dominant_count / len(known_domains), 4) if known_domains else 0.0

    return {
        "status": "ok",
        "source_count": len(items),
        "unique_domain_count": len(counts),
        "domain_distribution": ordered_counts,
        "dominant_domain": dominant_domain,
        "dominant_share": dominant_share,
        "unknown_domain_count": len(items) - len(known_domains),
        "is_concentrated": bool(known_domains and dominant_share > threshold),
        "message": (
            f"Audited {len(items)} sources across {len(counts)} unique domains; "
            f"dominant share is {dominant_share:.1%}."
        ),
    }

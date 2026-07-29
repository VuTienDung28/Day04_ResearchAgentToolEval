from __future__ import annotations

import re
import unicodedata
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
}


def _error(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "items": [],
        "removed_count": 0,
        "message": message,
    }


def _normalize_url(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return ""
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""

    hostname = (parsed.hostname or "").lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]
    port = parsed.port
    if port and not (
        (parsed.scheme.lower() == "http" and port == 80)
        or (parsed.scheme.lower() == "https" and port == 443)
    ):
        hostname = f"{hostname}:{port}"

    path = re.sub(r"/+", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")

    query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered.startswith("utm_") or lowered in TRACKING_QUERY_KEYS:
            continue
        query_pairs.append((key, value))
    query_pairs.sort()
    return urlunsplit(
        (
            parsed.scheme.lower(),
            hostname,
            path,
            urlencode(query_pairs, doseq=True),
            "",
        )
    )


def _normalize_title(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def deduplicate_sources(
    items: list[dict[str, Any]],
    match_by: str = "url_or_title",
) -> dict[str, Any]:
    """Return the first occurrence of each source under the selected matching rule."""
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        return _error("items must be a list of objects")
    if match_by not in {"url", "title", "url_or_title"}:
        return _error("match_by must be one of: url, title, url_or_title")

    kept: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    removed_count = 0

    for item in items:
        normalized_url = _normalize_url(item.get("url"))
        normalized_title = _normalize_title(item.get("title"))

        duplicate_url = bool(normalized_url and normalized_url in seen_urls)
        duplicate_title = bool(normalized_title and normalized_title in seen_titles)
        if match_by == "url":
            duplicate = duplicate_url
        elif match_by == "title":
            duplicate = duplicate_title
        else:
            duplicate = duplicate_url or duplicate_title

        if duplicate:
            removed_count += 1
            continue

        kept.append(dict(item))
        if normalized_url:
            seen_urls.add(normalized_url)
        if normalized_title:
            seen_titles.add(normalized_title)

    noun = "source" if removed_count == 1 else "sources"
    return {
        "status": "ok",
        "items": kept,
        "removed_count": removed_count,
        "message": f"Removed {removed_count} duplicate {noun}.",
    }

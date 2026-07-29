from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any


DATE_FIELDS = ("date", "published_at", "updated_at")


def _error(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "items": [],
        "undated_items": [],
        "dated_count": 0,
        "undated_count": 0,
        "message": message,
    }


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    candidates = [text]
    if text.endswith("Z"):
        candidates.insert(0, text[:-1] + "+00:00")
    for candidate in candidates:
        try:
            parsed = datetime.fromisoformat(candidate)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            pass
    try:
        parsed = parsedate_to_datetime(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def build_timeline(
    items: list[dict[str, Any]],
    order: str = "ascending",
) -> dict[str, Any]:
    """Sort supplied research items by a recognized date field."""
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        return _error("items must be a list of objects")
    if order not in {"ascending", "descending"}:
        return _error("order must be ascending or descending")

    dated: list[tuple[datetime, dict[str, Any]]] = []
    undated: list[dict[str, Any]] = []
    for item in items:
        parsed_date: datetime | None = None
        for field in DATE_FIELDS:
            parsed_date = _parse_date(item.get(field))
            if parsed_date is not None:
                break
        if parsed_date is None:
            undated.append(dict(item))
            continue
        enriched = dict(item)
        enriched["timeline_date"] = parsed_date.isoformat().replace("+00:00", "Z")
        dated.append((parsed_date, enriched))

    dated.sort(key=lambda pair: pair[0], reverse=order == "descending")
    timeline_items = [item for _, item in dated]
    return {
        "status": "ok",
        "items": timeline_items,
        "undated_items": undated,
        "dated_count": len(timeline_items),
        "undated_count": len(undated),
        "message": (
            f"Built a timeline with {len(timeline_items)} dated items "
            f"and {len(undated)} undated items."
        ),
    }

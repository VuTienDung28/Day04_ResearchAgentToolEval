from __future__ import annotations

from typing import Any


def _error(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "text": "",
        "citation_count": 0,
        "message": message,
    }


def _authors(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, list):
        names = [" ".join(str(item).split()) for item in value if str(item).strip()]
        return ", ".join(names)
    return ""


def _year(item: dict[str, Any]) -> str:
    for field in ("year", "published_at", "date"):
        value = item.get(field)
        if value is None:
            continue
        text = str(value).strip()
        if len(text) >= 4 and text[:4].isdigit():
            return text[:4]
    return "n.d."


def _citation(item: dict[str, Any], style: str, index: int) -> str:
    title = " ".join(str(item.get("title") or "Untitled source").split())
    url = str(item.get("url") or "").strip()
    source = " ".join(str(item.get("source") or "").split())
    authors = _authors(item.get("authors") or item.get("author"))
    year = _year(item)

    if style == "markdown":
        linked_title = f"[{title}]({url})" if url else title
        details = " — ".join(value for value in (authors, source, year) if value)
        return f"- {linked_title}" + (f" — {details}" if details else "")

    author_part = authors or source or "Unknown author"
    source_part = f" {source}." if source and source != author_part else ""
    url_part = f" {url}" if url else ""
    body = f'{author_part}. ({year}). "{title}."{source_part}{url_part}'.strip()
    return f"{index}. {body}" if style == "numbered" else body


def format_citations(
    items: list[dict[str, Any]],
    style: str = "markdown",
) -> dict[str, Any]:
    """Format supplied source metadata as Markdown, numbered, or APA-like citations."""
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        return _error("items must be a list of objects")
    if style not in {"markdown", "numbered", "apa"}:
        return _error("style must be one of: markdown, numbered, apa")

    citations = [_citation(item, style, index) for index, item in enumerate(items, start=1)]
    return {
        "status": "ok",
        "text": "\n".join(citations),
        "citation_count": len(citations),
        "message": f"Formatted {len(citations)} citations using {style} style.",
    }

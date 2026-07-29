from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit
from xml.etree import ElementTree

import requests

from tools._shared import TIMEOUT, domain


MAX_FEED_BYTES = 5_000_000
USER_AGENT = "Day04-Research-Agent-RSS/1.0"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _error(message: str) -> dict[str, Any]:
    return {"status": "error", "items": [], "message": message}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element: ElementTree.Element, *names: str) -> str:
    allowed = {name.lower() for name in names}
    for child in list(element):
        if _local_name(child.tag) in allowed:
            return "".join(child.itertext()).strip()
    return ""


def _entry_link(element: ElementTree.Element) -> str:
    for child in list(element):
        if _local_name(child.tag) != "link":
            continue
        href = (child.attrib.get("href") or "").strip()
        relation = (child.attrib.get("rel") or "alternate").lower()
        if href and relation in {"alternate", ""}:
            return href
        text = (child.text or "").strip()
        if text:
            return text
    return ""


def _plain_text(value: str, max_chars: int = 1000) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(value or "")
        text = " ".join(parser.parts)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", value or "")
    text = " ".join(unescape(text).split())
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


def read_rss_feed(feed_url: str, limit: int = 5) -> dict[str, Any]:
    """Read entries from a public RSS or Atom feed."""
    if not isinstance(feed_url, str):
        return _error("feed_url must be an absolute http or https URL")
    try:
        parsed = urlsplit(feed_url.strip())
    except ValueError:
        return _error("feed_url must be an absolute http or https URL")
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return _error("feed_url must be an absolute http or https URL")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
        return _error("limit must be an integer between 1 and 50")

    try:
        response = requests.get(
            feed_url.strip(),
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
        )
        response.raise_for_status()
        if len(response.content) > MAX_FEED_BYTES:
            return _error("feed response is larger than 5 MB")
        root = ElementTree.fromstring(response.content)
    except requests.RequestException as exc:
        return _error(f"Unable to download feed: {type(exc).__name__}")
    except ElementTree.ParseError:
        return _error("The URL did not return valid RSS or Atom XML")

    feed_title = _child_text(root, "title")
    entries = [
        element
        for element in root.iter()
        if _local_name(element.tag) in {"item", "entry"}
    ]

    items: list[dict[str, Any]] = []
    for entry in entries[:limit]:
        title = _plain_text(_child_text(entry, "title"), max_chars=300)
        url = _entry_link(entry)
        summary = _plain_text(_child_text(entry, "description", "summary", "content"))
        published_at = _child_text(entry, "pubdate", "published", "updated", "date")
        items.append(
            {
                "title": title,
                "url": url,
                "summary": summary,
                "published_at": published_at,
                "source": feed_title or domain(feed_url),
            }
        )

    return {
        "status": "ok",
        "items": items,
        "message": f"Returned {len(items)} feed entries.",
    }

"""Minimal arXiv Atom client (stdlib only)."""

from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
ARXIV_API = "https://export.arxiv.org/api/query"


@dataclass(frozen=True)
class Paper:
    arxiv_id: str
    title: str
    summary: str
    authors: tuple[str, ...]
    published: datetime
    updated: datetime
    pdf_url: str
    abs_url: str
    categories: tuple[str, ...]
    track_key: str
    score: float = 0.0


def _text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return " ".join(el.text.split())


def _parse_dt(value: str) -> datetime:
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _entry_to_paper(entry: ET.Element, track_key: str) -> Paper | None:
    id_url = _text(entry.find(f"{ATOM}id"))
    if not id_url:
        return None
    arxiv_id = id_url.rsplit("/", 1)[-1]

    title = _text(entry.find(f"{ATOM}title"))
    summary = _text(entry.find(f"{ATOM}summary"))
    authors = tuple(
        _text(a.find(f"{ATOM}name"))
        for a in entry.findall(f"{ATOM}author")
        if _text(a.find(f"{ATOM}name"))
    )
    published = _parse_dt(_text(entry.find(f"{ATOM}published")))
    updated = _parse_dt(_text(entry.find(f"{ATOM}updated")))

    pdf_url = ""
    abs_url = id_url
    for link in entry.findall(f"{ATOM}link"):
        rel = link.attrib.get("rel", "")
        href = link.attrib.get("href", "")
        title_attr = link.attrib.get("title", "")
        if title_attr == "pdf" or link.attrib.get("type") == "application/pdf":
            pdf_url = href
        elif rel == "alternate":
            abs_url = href
    if not pdf_url:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    categories = tuple(
        c.attrib.get("term", "")
        for c in entry.findall(f"{ATOM}category")
        if c.attrib.get("term")
    )

    return Paper(
        arxiv_id=arxiv_id,
        title=title,
        summary=summary,
        authors=authors,
        published=published,
        updated=updated,
        pdf_url=pdf_url,
        abs_url=abs_url,
        categories=categories,
        track_key=track_key,
    )


def search(
    query: str,
    *,
    track_key: str,
    max_results: int = 40,
    user_agent: str,
    sort_by: str = "submittedDate",
    sort_order: str = "descending",
) -> list[Paper]:
    params = urllib.parse.urlencode(
        {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }
    )
    url = f"{ARXIV_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})

    last_err: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = resp.read()
            break
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in {429, 500, 502, 503, 504}:
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError as exc:
            last_err = exc
            time.sleep(3 * (attempt + 1))
    else:
        assert last_err is not None
        raise last_err

    root = ET.fromstring(payload)
    papers: list[Paper] = []
    for entry in root.findall(f"{ATOM}entry"):
        paper = _entry_to_paper(entry, track_key)
        if paper:
            papers.append(paper)
    return papers

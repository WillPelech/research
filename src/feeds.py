"""Minimal RSS/Atom client (stdlib only)."""

from __future__ import annotations

import html
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class Post:
    feed_key: str
    title: str
    url: str
    summary: str
    published: datetime
    author: str | None = None


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _child(parent: ET.Element, *names: str) -> ET.Element | None:
    wanted = set(names)
    for child in parent:
        if _local(child.tag) in wanted:
            return child
    return None


def _children(parent: ET.Element, *names: str) -> list[ET.Element]:
    wanted = set(names)
    return [c for c in parent if _local(c.tag) in wanted]


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    raw = "".join(el.itertext()) if list(el) else (el.text or "")
    return WS_RE.sub(" ", raw).strip()


def _strip_html(value: str) -> str:
    text = html.unescape(TAG_RE.sub(" ", value))
    return WS_RE.sub(" ", text).strip()


def _parse_dt(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _link_from_atom(entry: ET.Element) -> str:
    for link in _children(entry, "link"):
        rel = link.attrib.get("rel", "alternate")
        href = link.attrib.get("href", "").strip()
        if href and rel in {"alternate", ""}:
            return href
    for link in _children(entry, "link"):
        href = link.attrib.get("href", "").strip()
        if href:
            return href
    return _text(_child(entry, "id"))


def _summary_from_entry(entry: ET.Element) -> str:
    for child in entry:
        local = _local(child.tag)
        if local in {"summary", "description", "content", "encoded"}:
            return _strip_html(_text(child) or (child.text or ""))
    return ""


def _parse_rss_item(item: ET.Element, feed_key: str) -> Post | None:
    title = _strip_html(_text(_child(item, "title")))
    link = _text(_child(item, "link"))
    if not link:
        guid = _child(item, "guid")
        if guid is not None and guid.attrib.get("isPermaLink", "true") != "false":
            link = _text(guid)
    if not title or not link:
        return None

    published = None
    for name in ("pubDate", "published", "updated", "dc:date", "date"):
        for child in item:
            if _local(child.tag) in {"pubDate", "published", "updated", "date"}:
                published = _parse_dt(_text(child))
                if published:
                    break
        if published:
            break
    if published is None:
        published = datetime.now(timezone.utc)

    author = _text(_child(item, "author", "dc:creator", "creator")) or None
    summary = _summary_from_entry(item)
    return Post(
        feed_key=feed_key,
        title=title,
        url=link,
        summary=summary,
        published=published,
        author=author or None,
    )


def _parse_atom_entry(entry: ET.Element, feed_key: str) -> Post | None:
    title = _strip_html(_text(_child(entry, "title")))
    link = _link_from_atom(entry)
    if not title or not link:
        return None

    published = None
    for child in entry:
        if _local(child.tag) in {"published", "updated"}:
            published = _parse_dt(_text(child))
            if published:
                break
    if published is None:
        published = datetime.now(timezone.utc)

    author_el = _child(entry, "author")
    author = _text(_child(author_el, "name")) if author_el is not None else None
    summary = _summary_from_entry(entry)
    return Post(
        feed_key=feed_key,
        title=title,
        url=link,
        summary=summary,
        published=published,
        author=author or None,
    )


def parse_feed(payload: bytes, feed_key: str) -> list[Post]:
    root = ET.fromstring(payload)
    posts: list[Post] = []

    # RSS 2.0
    for channel in root.iter():
        if _local(channel.tag) != "channel":
            continue
        for item in _children(channel, "item"):
            post = _parse_rss_item(item, feed_key)
            if post:
                posts.append(post)
        if posts:
            return posts

    # Atom
    if _local(root.tag) == "feed":
        for entry in _children(root, "entry"):
            post = _parse_atom_entry(entry, feed_key)
            if post:
                posts.append(post)
        return posts

    # Fallback: any item/entry anywhere
    for el in root.iter():
        local = _local(el.tag)
        if local == "item":
            post = _parse_rss_item(el, feed_key)
            if post:
                posts.append(post)
        elif local == "entry":
            post = _parse_atom_entry(el, feed_key)
            if post:
                posts.append(post)
    return posts


def fetch_feed(url: str, *, feed_key: str, user_agent: str) -> list[Post]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        },
    )
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = resp.read()
            return parse_feed(payload, feed_key)
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in {429, 500, 502, 503, 504}:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError as exc:
            last_err = exc
            time.sleep(2 * (attempt + 1))
    assert last_err is not None
    raise last_err

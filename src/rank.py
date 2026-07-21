"""Select recent posts per feed."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .config import Feed
from .feeds import Post


def select_posts(
    posts: list[Post],
    feed: Feed,
    *,
    now: datetime | None = None,
) -> list[Post]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=feed.lookback_days)

    recent = [p for p in posts if p.published >= cutoff]
    recent.sort(key=lambda p: p.published, reverse=True)

    seen: set[str] = set()
    picked: list[Post] = []
    for post in recent:
        key = post.url.rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        picked.append(post)
        if len(picked) >= feed.max_items:
            break
    return picked

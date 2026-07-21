"""Render markdown and HTML digests."""

from __future__ import annotations

import html
from datetime import datetime
from typing import Iterable

from .config import Feed
from .feeds import Post


def _blurb(post: Post, limit: int = 280) -> str:
    text = post.summary.strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def render_markdown(
    *,
    week_label: str,
    generated_at: datetime,
    sections: list[tuple[Feed, list[Post]]],
) -> str:
    total = sum(len(posts) for _, posts in sections)
    lines = [
        f"# AI Research Digest — {week_label}",
        "",
        f"_Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')} · {total} posts_",
        "",
        "Curated picks from frontier labs, open-source, and educator blogs.",
        "",
    ]
    for feed, posts in sections:
        lines.append(f"## {feed.title}")
        lines.append("")
        lines.append(f"_{feed.author} · {feed.focus} · {feed.cadence}_")
        lines.append("")
        if not posts:
            lines.append("_No new posts in the lookback window._")
            lines.append("")
            continue
        for i, post in enumerate(posts, 1):
            blurb = _blurb(post)
            meta = f"**Published:** {post.published.date().isoformat()}"
            if post.author:
                meta += f" · **By:** {post.author}"
            lines.extend(
                [
                    f"### {i}. [{post.title}]({post.url})",
                    "",
                    meta,
                    "",
                ]
            )
            if blurb:
                lines.append(blurb)
                lines.append("")
            lines.append(f"[Read]({post.url})")
            lines.append("")
    lines.extend(
        [
            "---",
            "",
            "_Sources: official RSS/Atom feeds. No arXiv._",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(
    *,
    week_label: str,
    generated_at: datetime,
    sections: list[tuple[Feed, list[Post]]],
) -> str:
    total = sum(len(posts) for _, posts in sections)
    parts: list[str] = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>AI Research Digest — {html.escape(week_label)}</title>",
        "</head><body style='font-family:Georgia,serif;line-height:1.5;"
        "color:#1a1a1a;max-width:720px;margin:0 auto;padding:24px;'>",
        f"<h1 style='font-size:1.6rem;margin-bottom:0.2rem;'>"
        f"AI Research Digest — {html.escape(week_label)}</h1>",
        f"<p style='color:#555;margin-top:0;'>"
        f"Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')} · {total} posts</p>",
        "<p>Curated picks from frontier labs, open-source, and educator blogs.</p>",
    ]

    for feed, posts in sections:
        parts.append(
            f"<h2 style='border-bottom:1px solid #ddd;padding-bottom:4px;'>"
            f"{html.escape(feed.title)}</h2>"
        )
        parts.append(
            f"<p style='color:#555;margin-top:0;font-size:0.95rem;'>"
            f"{html.escape(feed.author)} · {html.escape(feed.focus)} · "
            f"{html.escape(feed.cadence)}</p>"
        )
        if not posts:
            parts.append("<p><em>No new posts in the lookback window.</em></p>")
            continue
        for i, post in enumerate(posts, 1):
            blurb = _blurb(post)
            meta = f"Published {post.published.date().isoformat()}"
            if post.author:
                meta += f" · By {html.escape(post.author)}"
            parts.extend(
                [
                    "<div style='margin:1.2rem 0;'>",
                    f"<h3 style='margin-bottom:0.35rem;font-size:1.1rem;'>"
                    f"{i}. <a href='{html.escape(post.url)}'>"
                    f"{html.escape(post.title)}</a></h3>",
                    f"<p style='margin:0.2rem 0;color:#444;font-size:0.95rem;'>"
                    f"{meta}</p>",
                ]
            )
            if blurb:
                parts.append(
                    f"<p style='margin:0.55rem 0;'>{html.escape(blurb)}</p>"
                )
            parts.append(
                f"<p style='margin:0;'><a href='{html.escape(post.url)}'>Read</a></p>"
                "</div>"
            )

    parts.extend(
        [
            "<hr style='border:none;border-top:1px solid #ddd;margin:2rem 0;'>",
            "<p style='color:#666;font-size:0.9rem;'>"
            "Sources: official RSS/Atom feeds. No arXiv.</p>",
            "</body></html>",
        ]
    )
    return "".join(parts)


def subject_line(week_label: str, sections: Iterable[tuple[Feed, list[Post]]]) -> str:
    total = sum(len(posts) for _, posts in sections)
    active = sum(1 for _, posts in sections if posts)
    return f"AI Research Digest — {week_label} ({total} posts · {active} sources)"

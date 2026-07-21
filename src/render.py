"""Render markdown and HTML digests."""

from __future__ import annotations

import html
from datetime import datetime
from typing import Iterable

from .arxiv_client import Paper
from .config import Track


def _authors(paper: Paper, limit: int = 4) -> str:
    names = list(paper.authors)
    if len(names) <= limit:
        return ", ".join(names)
    return ", ".join(names[:limit]) + f" +{len(names) - limit} more"


def _blurb(paper: Paper, limit: int = 320) -> str:
    text = paper.summary.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def render_markdown(
    *,
    week_label: str,
    generated_at: datetime,
    sections: list[tuple[Track, list[Paper]]],
) -> str:
    lines = [
        f"# Research Digest — {week_label}",
        "",
        f"_Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "Lightweight weekly picks from arXiv: **AI models** and **harness / agent** research.",
        "",
    ]
    for track, papers in sections:
        lines.append(f"## {track.title}")
        lines.append("")
        if not papers:
            lines.append("_No strong matches in the lookback window._")
            lines.append("")
            continue
        for i, paper in enumerate(papers, 1):
            cats = ", ".join(paper.categories[:4]) or "n/a"
            lines.extend(
                [
                    f"### {i}. [{paper.title}]({paper.abs_url})",
                    "",
                    f"**Authors:** {_authors(paper)}  ",
                    f"**Published:** {paper.published.date().isoformat()} · "
                    f"**Categories:** {cats} · "
                    f"**Score:** {paper.score:.1f}",
                    "",
                    _blurb(paper),
                    "",
                    f"[Abstract]({paper.abs_url}) · [PDF]({paper.pdf_url})",
                    "",
                ]
            )
    lines.append("---")
    lines.append("")
    lines.append("_Source: arXiv API. Ranked by topical relevance + recency._")
    lines.append("")
    return "\n".join(lines)


def render_html(
    *,
    week_label: str,
    generated_at: datetime,
    sections: list[tuple[Track, list[Paper]]],
) -> str:
    parts: list[str] = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>Research Digest — {html.escape(week_label)}</title>",
        "</head><body style='font-family:Georgia,serif;line-height:1.5;"
        "color:#1a1a1a;max-width:720px;margin:0 auto;padding:24px;'>",
        f"<h1 style='font-size:1.6rem;margin-bottom:0.2rem;'>"
        f"Research Digest — {html.escape(week_label)}</h1>",
        f"<p style='color:#555;margin-top:0;'>"
        f"Generated {generated_at.strftime('%Y-%m-%d %H:%M UTC')}</p>",
        "<p>Lightweight weekly picks from arXiv covering "
        "<strong>AI models</strong> and <strong>harness / agent</strong> research.</p>",
    ]

    for track, papers in sections:
        parts.append(f"<h2 style='border-bottom:1px solid #ddd;padding-bottom:4px;'>"
                     f"{html.escape(track.title)}</h2>")
        if not papers:
            parts.append("<p><em>No strong matches in the lookback window.</em></p>")
            continue
        for i, paper in enumerate(papers, 1):
            cats = ", ".join(paper.categories[:4]) or "n/a"
            parts.extend(
                [
                    "<div style='margin:1.4rem 0;'>",
                    f"<h3 style='margin-bottom:0.35rem;font-size:1.1rem;'>"
                    f"{i}. <a href='{html.escape(paper.abs_url)}'>"
                    f"{html.escape(paper.title)}</a></h3>",
                    "<p style='margin:0.2rem 0;color:#444;font-size:0.95rem;'>",
                    f"<strong>Authors:</strong> {html.escape(_authors(paper))}<br>",
                    f"<strong>Published:</strong> {paper.published.date().isoformat()} · ",
                    f"<strong>Categories:</strong> {html.escape(cats)} · ",
                    f"<strong>Score:</strong> {paper.score:.1f}",
                    "</p>",
                    f"<p style='margin:0.6rem 0;'>{html.escape(_blurb(paper))}</p>",
                    "<p style='margin:0;'>",
                    f"<a href='{html.escape(paper.abs_url)}'>Abstract</a> · ",
                    f"<a href='{html.escape(paper.pdf_url)}'>PDF</a>",
                    "</p></div>",
                ]
            )

    parts.extend(
        [
            "<hr style='border:none;border-top:1px solid #ddd;margin:2rem 0;'>",
            "<p style='color:#666;font-size:0.9rem;'>"
            "Source: arXiv API. Ranked by topical relevance + recency.</p>",
            "</body></html>",
        ]
    )
    return "".join(parts)


def subject_line(week_label: str, sections: Iterable[tuple[Track, list[Paper]]]) -> str:
    total = sum(len(papers) for _, papers in sections)
    return f"Research Digest — {week_label} ({total} papers)"

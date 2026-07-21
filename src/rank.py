"""Score and select the best recent papers per track."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .arxiv_client import Paper
from .config import Track


def _norm(text: str) -> str:
    return " ".join(text.lower().split())


def score_paper(paper: Paper, track: Track, now: datetime) -> float:
    """Higher is better. Blends topical boosts with recency."""
    blob = _norm(f"{paper.title} {paper.summary}")
    score = 0.0

    for i, term in enumerate(track.boost_terms):
        weight = max(1.0, 3.0 - i * 0.15)
        if term in blob:
            # Title hits matter more than abstract-only.
            if term in _norm(paper.title):
                score += weight * 2.2
            else:
                score += weight

    age_days = max(0.0, (now - paper.published).total_seconds() / 86400.0)
    # Prefer papers from this week; soft decay after that.
    score += max(0.0, 4.0 - age_days * 0.35)

    # Mild preference for core AI venues/categories.
    hot = {"cs.LG", "cs.CL", "cs.AI", "cs.SE"}
    score += 0.35 * sum(1 for c in paper.categories if c in hot)
    return score


def select_papers(
    papers: list[Paper],
    track: Track,
    *,
    lookback_days: int,
    top_n: int,
    now: datetime | None = None,
) -> list[Paper]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=lookback_days)

    recent = [p for p in papers if p.published >= cutoff]
    scored: list[Paper] = []
    for paper in recent:
        scored.append(
            Paper(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                summary=paper.summary,
                authors=paper.authors,
                published=paper.published,
                updated=paper.updated,
                pdf_url=paper.pdf_url,
                abs_url=paper.abs_url,
                categories=paper.categories,
                track_key=paper.track_key,
                score=score_paper(paper, track, now),
            )
        )

    scored.sort(key=lambda p: (p.score, p.published), reverse=True)

    seen: set[str] = set()
    picked: list[Paper] = []
    for paper in scored:
        base_id = paper.arxiv_id.split("v")[0]
        if base_id in seen:
            continue
        seen.add(base_id)
        picked.append(paper)
        if len(picked) >= top_n:
            break
    return picked

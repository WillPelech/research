"""Build and optionally email a weekly AI blog digest."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .config import FEEDS, Settings
from .emailer import send_email
from .feeds import fetch_feed
from .rank import select_posts
from .render import render_html, render_markdown, subject_line


def week_label(now: datetime) -> str:
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def build_digest(settings: Settings) -> tuple[str, str, str, Path]:
    now = datetime.now(timezone.utc)
    label = week_label(now)
    sections: list = []

    for i, feed in enumerate(FEEDS):
        if i:
            time.sleep(0.4)
        print(f"Fetching: {feed.title}", flush=True)
        try:
            raw = fetch_feed(
                feed.url, feed_key=feed.key, user_agent=settings.user_agent
            )
            picked = select_posts(raw, feed, now=now)
            print(f"  fetched={len(raw)} selected={len(picked)}", flush=True)
        except Exception as exc:  # noqa: BLE001 — keep other feeds going
            print(f"  ERROR: {exc}", flush=True)
            picked = []
        sections.append((feed, picked))

    # Drop empty sources from the email to keep it readable;
    # still mention empty ones lightly in markdown archive.
    md = render_markdown(week_label=label, generated_at=now, sections=sections)
    email_sections = [(f, p) for f, p in sections if p]
    if not email_sections:
        email_sections = sections
    html = render_html(week_label=label, generated_at=now, sections=email_sections)
    subject = subject_line(label, sections)

    out_dir = Path(__file__).resolve().parent.parent / "digests"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{label}.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote {out_path}", flush=True)
    return subject, html, md, out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Weekly AI research blog digest")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build digest without sending email",
    )
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    if args.dry_run:
        settings = Settings(
            to_email=settings.to_email or "dry-run@example.com",
            from_email=settings.from_email,
            resend_api_key=settings.resend_api_key,
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_password=settings.smtp_password,
            smtp_use_tls=settings.smtp_use_tls,
            dry_run=True,
            user_agent=settings.user_agent,
        )
    else:
        settings.require_mail_config()

    subject, html, md, _path = build_digest(settings)
    send_email(settings, subject=subject, html_body=html, text_body=md)
    return 0


if __name__ == "__main__":
    sys.exit(main())

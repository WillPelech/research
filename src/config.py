"""Weekly AI blog digest configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Feed:
    """A curated blog / research feed."""

    key: str
    title: str
    author: str
    focus: str
    cadence: str
    url: str
    # How far back to include posts from this source (days).
    lookback_days: int
    # Cap posts per source so high-volume feeds don't dominate.
    max_items: int


# Curated sources — RSS only, no arXiv.
FEEDS: tuple[Feed, ...] = (
    Feed(
        key="openai",
        title="OpenAI Blog",
        author="OpenAI Research Team",
        focus="Frontier AI research, safety, product updates",
        cadence="Weekly",
        url="https://openai.com/news/rss.xml",
        lookback_days=7,
        max_items=5,
    ),
    Feed(
        key="deepmind",
        title="Google DeepMind Blog",
        author="DeepMind Research Team",
        focus="Scientific AI, reinforcement learning, breakthroughs",
        cadence="Weekly",
        url="https://deepmind.google/blog/rss.xml",
        lookback_days=7,
        max_items=5,
    ),
    Feed(
        key="lilian_weng",
        title="Lilian Weng's Blog",
        author="Lilian Weng (OpenAI)",
        focus="Technical deep dives and concept explainers",
        cadence="Monthly",
        url="https://lilianweng.github.io/index.xml",
        lookback_days=35,
        max_items=2,
    ),
    Feed(
        key="ahead_of_ai",
        title="Ahead of AI",
        author="Sebastian Raschka",
        focus="LLM implementation, hands-on tutorials and code",
        cadence="Weekly",
        url="https://magazine.sebastianraschka.com/feed",
        lookback_days=7,
        max_items=3,
    ),
    Feed(
        key="jay_alammar",
        title="Jay Alammar's Blog",
        author="Jay Alammar",
        focus="Visual AI education for beginners and practitioners",
        cadence="Monthly",
        url="https://jalammar.github.io/feed.xml",
        lookback_days=35,
        max_items=2,
    ),
    Feed(
        key="huggingface",
        title="Hugging Face Blog",
        author="Hugging Face Team",
        focus="Open-source models, releases, and tutorials",
        cadence="Multiple per week",
        url="https://huggingface.co/blog/feed.xml",
        lookback_days=7,
        max_items=5,
    ),
    Feed(
        key="gradient",
        title="The Gradient",
        author="AI Research Community",
        focus="Research analysis, paper summaries, interviews",
        cadence="Weekly",
        url="https://thegradient.pub/rss/",
        lookback_days=14,
        max_items=3,
    ),
    Feed(
        key="bair",
        title="BAIR Blog",
        author="UC Berkeley AI Research",
        focus="Cutting-edge academic AI research",
        cadence="Bi-weekly",
        url="https://bair.berkeley.edu/blog/feed.xml",
        lookback_days=14,
        max_items=3,
    ),
    Feed(
        key="karpathy",
        title="Andrej Karpathy's Blog",
        author="Andrej Karpathy",
        focus="Deep learning systems and practical ML",
        cadence="Occasional",
        url="https://karpathy.github.io/feed.xml",
        lookback_days=60,
        max_items=2,
    ),
)


@dataclass(frozen=True)
class Settings:
    to_email: str
    from_email: str
    resend_api_key: str | None
    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_password: str | None
    smtp_use_tls: bool
    dry_run: bool
    user_agent: str

    @classmethod
    def from_env(cls) -> Settings:
        to_email = os.environ.get("DIGEST_TO_EMAIL", "").strip()
        from_email = (
            os.environ.get("DIGEST_FROM_EMAIL", "").strip()
            or "Research Digest <onboarding@resend.dev>"
        )
        dry = os.environ.get("DRY_RUN", "0").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        smtp_port_raw = os.environ.get("SMTP_PORT", "").strip() or "587"
        smtp_tls_raw = os.environ.get("SMTP_USE_TLS", "").strip() or "true"
        return cls(
            to_email=to_email,
            from_email=from_email,
            resend_api_key=os.environ.get("RESEND_API_KEY") or None,
            smtp_host=os.environ.get("SMTP_HOST") or None,
            smtp_port=int(smtp_port_raw),
            smtp_user=os.environ.get("SMTP_USER") or None,
            smtp_password=os.environ.get("SMTP_PASSWORD") or None,
            smtp_use_tls=smtp_tls_raw.lower() in {"1", "true", "yes"},
            dry_run=dry,
            user_agent=os.environ.get(
                "DIGEST_USER_AGENT",
                "research-digest/1.0 (github.com/WillPelech/research)",
            ),
        )

    def require_mail_config(self) -> None:
        if self.dry_run:
            return
        if not self.to_email:
            raise SystemExit("DIGEST_TO_EMAIL is required")
        if self.resend_api_key:
            return
        if self.smtp_host and self.smtp_user and self.smtp_password:
            return
        raise SystemExit(
            "Configure RESEND_API_KEY or SMTP_HOST/SMTP_USER/SMTP_PASSWORD"
        )

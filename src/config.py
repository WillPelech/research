"""Weekly research digest configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    """A topical search bucket for the digest."""

    key: str
    title: str
    query: str
    boost_terms: tuple[str, ...]


# Lightweight arXiv queries: recent + relevant, not exhaustive.
TRACKS: tuple[Track, ...] = (
    Track(
        key="ai_models",
        title="AI Models",
        query=(
            "(cat:cs.LG OR cat:cs.CL OR cat:cs.AI OR cat:cs.CV) AND "
            "(ti:\"large language model\" OR ti:\"foundation model\" OR "
            'ti:"language model" OR ti:LLM OR abs:"foundation model" OR '
            'ti:multimodal OR ti:"mixture of experts" OR ti:MoE OR '
            'ti:reasoning OR abs:"chain of thought")'
        ),
        boost_terms=(
            "foundation model",
            "large language model",
            "llm",
            "multimodal",
            "mixture of experts",
            "reasoning",
            "scaling",
            "alignment",
            "post-training",
            "rlhf",
            "inference",
        ),
    ),
    Track(
        key="harness",
        title="Harness & Agents",
        query=(
            "(cat:cs.AI OR cat:cs.LG OR cat:cs.SE OR cat:cs.CL) AND "
            '(ti:harness OR ti:agent OR abs:"agentic" OR ti:scaffold OR '
            'ti:"tool use" OR ti:tool-use OR ti:"software engineering" OR '
            'ti:SWE-bench OR abs:"coding agent" OR abs:"evaluation harness" OR '
            'abs:"agent framework" OR ti:benchmark)'
        ),
        boost_terms=(
            "harness",
            "agent",
            "agentic",
            "scaffold",
            "tool use",
            "tool-calling",
            "swe-bench",
            "coding agent",
            "evaluation harness",
            "agent framework",
            "orchestration",
            "multi-agent",
        ),
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
    lookback_days: int
    top_per_track: int
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
        lookback_raw = os.environ.get("LOOKBACK_DAYS", "").strip() or "7"
        top_raw = os.environ.get("TOP_PER_TRACK", "").strip() or "6"
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
            lookback_days=int(lookback_raw),
            top_per_track=int(top_raw),
            dry_run=dry,
            user_agent=os.environ.get(
                "ARXIV_USER_AGENT",
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

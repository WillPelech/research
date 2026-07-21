"""Send digest email via Resend or SMTP."""

from __future__ import annotations

import json
import smtplib
import ssl
import urllib.error
import urllib.request
from email.message import EmailMessage

from .config import Settings


def send_email(
    settings: Settings,
    *,
    subject: str,
    html_body: str,
    text_body: str,
) -> None:
    if settings.dry_run:
        print("[dry-run] Skipping send")
        print(f"To: {settings.to_email}")
        print(f"Subject: {subject}")
        return

    if settings.resend_api_key:
        _send_resend(settings, subject=subject, html_body=html_body, text_body=text_body)
        return

    _send_smtp(settings, subject=subject, html_body=html_body, text_body=text_body)


def _send_resend(
    settings: Settings,
    *,
    subject: str,
    html_body: str,
    text_body: str,
) -> None:
    payload = {
        "from": settings.from_email,
        "to": [settings.to_email],
        "subject": subject,
        "html": html_body,
        "text": text_body,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
            "User-Agent": settings.user_agent,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Resend failed ({exc.code}): {detail}") from exc
    print(f"Sent via Resend: {body}")


def _send_smtp(
    settings: Settings,
    *,
    subject: str,
    html_body: str,
    text_body: str,
) -> None:
    assert settings.smtp_host and settings.smtp_user and settings.smtp_password

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.from_email
    msg["To"] = settings.to_email
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    if settings.smtp_use_tls:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=45) as smtp:
            smtp.starttls(context=context)
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=45) as smtp:
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)
    print(f"Sent via SMTP to {settings.to_email}")

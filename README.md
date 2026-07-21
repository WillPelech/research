# Research Digest

Weekly email of the best new arXiv papers on **AI models** and **harness / agent** research. Runs on GitHub Actions — nothing to leave running on your machine.

## What you get

Every Monday, the workflow:

1. Searches arXiv for recent papers in two tracks (AI models, harness & agents)
2. Scores them by topical relevance + recency and keeps the top picks
3. Emails you an HTML digest
4. Commits a markdown copy under [`digests/`](digests/) so you can also read it on GitHub

## One-time setup

### 1. Push this repo to GitHub

```bash
git add .
git commit -m "Add weekly research digest"
git push -u origin main
```

### 2. Configure email secrets

In the GitHub repo: **Settings → Secrets and variables → Actions**.

**Recommended (Resend, free tier):**

| Secret | Value |
| --- | --- |
| `DIGEST_TO_EMAIL` | Your inbox |
| `DIGEST_FROM_EMAIL` | A verified Resend from-address, e.g. `Research Digest <digest@yourdomain.com>` |
| `RESEND_API_KEY` | From [resend.com](https://resend.com) |

For a quick test you can use Resend’s onboarding sender (`onboarding@resend.dev`) and send only to the email you signed up with.

**Or SMTP** (omit `RESEND_API_KEY`):

| Secret | Example |
| --- | --- |
| `DIGEST_TO_EMAIL` | `you@example.com` |
| `DIGEST_FROM_EMAIL` | `you@gmail.com` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | your Gmail address |
| `SMTP_PASSWORD` | Gmail app password |
| `SMTP_USE_TLS` | `true` |

### 3. Run it

- **Automatically:** Mondays at 13:00 UTC
- **Manually:** Actions → *Weekly Research Digest* → *Run workflow*

## Local preview

No dependencies beyond Python 3.11+:

```bash
python run_digest.py --dry-run
```

That writes `digests/<year>-W<week>.md` without sending mail. Copy `.env.example` → `.env` and export vars if you want a real local send.

## Tuning

| Env var | Default | Meaning |
| --- | --- | --- |
| `LOOKBACK_DAYS` | `7` | How far back to consider papers |
| `TOP_PER_TRACK` | `6` | Max papers per track |

Queries and boost terms live in [`src/config.py`](src/config.py).

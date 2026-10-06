# AI Research Digest

Weekly email of new posts from a curated set of AI research blogs. Runs on GitHub Actions — nothing to leave running on your machine.

## Sources

| Source | Focus | Cadence |
| --- | --- | --- |
| [OpenAI Blog](https://openai.com/news/) | Frontier research, safety, updates | Weekly |
| [Google DeepMind](https://deepmind.google/blog/) | Scientific AI, RL | Weekly |
| [Lilian Weng](https://lilianweng.github.io/) | Technical deep dives | Monthly |
| [Ahead of AI](https://magazine.sebastianraschka.com/) | LLM implementation / tutorials | Weekly |
| [Jay Alammar](https://jalammar.github.io/) | Visual AI explainers | Monthly |
| [Hugging Face](https://huggingface.co/blog) | Open-source models & tutorials | Multiple / week |
| [The Gradient](https://thegradient.pub/) | Research analysis | Weekly |
| [BAIR Blog](https://bair.berkeley.edu/blog/) | Academic research | Bi-weekly |
| [Andrej Karpathy](https://karpathy.github.io/) | DL systems, practical ML | Occasional |

All posts are pulled from each site’s official RSS/Atom feed (configured in [`src/config.py`](src/config.py)).

## What you get

Every Monday, the workflow:

1. Fetches each feed
2. Keeps recent posts (lookback varies by cadence; high-volume feeds are capped)
3. Emails every recipient an HTML digest grouped by source
4. Commits a markdown copy under [`digests/`](digests/)

## One-time setup

### 1. Push this repo to GitHub

```bash
git add .
git commit -m "Switch digest to curated AI blogs"
git push
```

### 2. Configure email secrets

In the GitHub repo: **Settings → Secrets and variables → Actions**.

**Recommended (Resend):**

| Secret | Value |
| --- | --- |
| `DIGEST_TO_EMAIL` | Your inbox (comma-separate for several recipients) |
| `DIGEST_EXTRA_EMAILS` | Optional extra recipients, merged with the above |
| `DIGEST_FROM_EMAIL` | Verified Resend from-address |
| `RESEND_API_KEY` | From [resend.com](https://resend.com) |

**Or SMTP:** `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_USE_TLS`.

Set the repo **variable** `DIGEST_EMAIL_PROVIDER` to `smtp` to force the SMTP path, or
`resend` to force Resend. Left unset it defaults to `auto`, which uses Resend whenever
`RESEND_API_KEY` is present.

> Note: Resend only delivers to your own address until you verify a domain at
> [resend.com/domains](https://resend.com/domains). With multiple recipients on an
> unverified account the whole send fails, so use SMTP or verify a domain first.

### 3. Run it

- **Automatically:** Mondays at 13:00 UTC
- **Manually:** Actions → *Weekly Research Digest* → *Run workflow*

## Local preview

Python 3.11+, no third-party packages:

```bash
python run_digest.py --dry-run
```

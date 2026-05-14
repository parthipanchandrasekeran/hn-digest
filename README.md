# Hacker News Daily Digest

A small, production-ready scraper that pulls top stories from [news.ycombinator.com](https://news.ycombinator.com/), filters by score, and writes a daily CSV. Runs on **GitHub Actions** — commits a new CSV every day, zero hosting cost.

> **What this demonstrates:** Clean Python scraping, sensible tool choice (`requests` vs Playwright), scheduled execution via GitHub Actions, idempotent CSV output.

## Sample run

```text
$ python scrape.py --min-points 100
Scraping HN (min_points=100, limit=30)...
Matched 14 stories.
Wrote data/hn-2026-05-14.csv
```

See [`data/`](./data) for daily digests committed by CI.

## Why `requests` + `BeautifulSoup` (not Playwright)

HN serves static, server-rendered HTML. A headless browser would add ~5s of startup and 200MB of dependencies for zero benefit.

For **JavaScript-rendered sites** (React, Vue, infinite scroll, anti-bot), the right tool is Playwright. See [`PLAYWRIGHT_NOTES.md`](./PLAYWRIGHT_NOTES.md) for that pattern.

Engineering judgment is the gig, not "use the fanciest tool."

## Run locally

```bash
pip install -r requirements.txt
python scrape.py --min-points 100
```

## Run on a schedule (free, no server)

The included [`.github/workflows/daily.yml`](.github/workflows/daily.yml) runs the scraper at 14:00 UTC daily and commits the CSV back to the repo.

To enable on your fork:

1. Fork this repo.
2. Settings → Actions → General → "Allow all actions and reusable workflows."
3. Settings → Actions → General → Workflow permissions → **Read and write permissions**.
4. The workflow runs daily automatically. Trigger manually any time from the **Actions** tab.

## CLI options

```
--min-points N   Minimum score to include      (default: 100)
--limit N        Max rows to scan from front   (default: 30)
--out PATH       Output CSV path               (default: data/hn-YYYY-MM-DD.csv)
```

## CSV schema

| column | type | notes |
|---|---|---|
| `id` | string | HN story id |
| `title` | string | Story title |
| `url` | string | Outbound link (may be `item?id=…` for Ask/Show HN) |
| `points` | int | Score at scrape time |
| `author` | string | HN username |
| `comments` | int | Comment count at scrape time |
| `hn_link` | string | Permalink to the HN thread |
| `scraped_at` | ISO 8601 | UTC timestamp |

## Built by Parthipan Chandrasekaran

I build automations like this for clients — n8n workflows, custom scrapers, Chrome extensions, AI integrations.

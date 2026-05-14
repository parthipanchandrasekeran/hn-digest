"""
Hacker News Daily Digest Scraper

Scrapes top stories from news.ycombinator.com, filters by score, and writes
a daily CSV. Designed to run on a schedule via GitHub Actions.

Why requests + BeautifulSoup (not Playwright):
    HN serves static, server-rendered HTML. A headless browser would add
    ~5s of startup and 200MB of dependencies for zero benefit. For
    JavaScript-rendered sites (React/Vue/infinite scroll), switch to
    Playwright — the pattern is in PLAYWRIGHT_NOTES.md.

Engineering judgment is the gig, not "use the fanciest tool."
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HN_URL = "https://news.ycombinator.com/"
USER_AGENT = "hn-digest-scraper/1.0 (+https://github.com/yourname/hn-digest)"


def scrape_hn(min_points: int = 100, limit: int = 30) -> list[dict]:
    """Scrape HN front page; return stories with score >= min_points."""
    resp = requests.get(HN_URL, headers={"User-Agent": USER_AGENT}, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    stories: list[dict] = []
    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for row in soup.select("tr.athing")[:limit]:
        story_id = row.get("id", "")
        title_link = row.select_one("span.titleline > a")
        if not title_link:
            continue

        title = title_link.get_text(strip=True)
        url = title_link.get("href", "")

        # Subtext lives in the next <tr> sibling
        subtext_row = row.find_next_sibling("tr")
        if not subtext_row:
            continue

        score_el = subtext_row.select_one(".score")
        points = _parse_leading_int(score_el.get_text()) if score_el else 0
        if points < min_points:
            continue

        author_el = subtext_row.select_one(".hnuser")
        author = author_el.get_text(strip=True) if author_el else ""

        comments = 0
        for link in subtext_row.select("a"):
            text = link.get_text(strip=True)
            if "comment" in text.lower():
                comments = _parse_leading_int(text)
                break

        stories.append(
            {
                "id": story_id,
                "title": title,
                "url": url,
                "points": points,
                "author": author,
                "comments": comments,
                "hn_link": f"https://news.ycombinator.com/item?id={story_id}",
                "scraped_at": scraped_at,
            }
        )

    return stories


def _parse_leading_int(text: str) -> int:
    """Return the leading integer in a string, or 0 if none."""
    head = text.strip().split()[0] if text.strip() else "0"
    return int(head) if head.isdigit() else 0


def write_csv(stories: list[dict], out_path: Path) -> None:
    """Write stories to a CSV, creating parents as needed."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not stories:
        print("No stories matched filter; nothing written.", file=sys.stderr)
        return
    fields = list(stories[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(stories)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape HN top stories into a CSV.")
    parser.add_argument("--min-points", type=int, default=100, help="Minimum score (default: 100).")
    parser.add_argument("--limit", type=int, default=30, help="Max rows to scan (default: 30).")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data") / f"hn-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()

    print(f"Scraping HN (min_points={args.min_points}, limit={args.limit})...")
    stories = scrape_hn(min_points=args.min_points, limit=args.limit)
    print(f"Matched {len(stories)} stories.")

    write_csv(stories, args.out)
    if stories:
        print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# When to reach for Playwright

The main scraper in this repo uses `requests` + `BeautifulSoup` because Hacker News serves static HTML. For sites that **render content with JavaScript**, those tools see an empty shell. That's when you switch to Playwright (or Selenium).

## Signs you need a real browser

- `view-source:` of the page is mostly `<div id="root"></div>` with no data
- The page makes XHR/fetch calls *after* page load that populate the content
- Infinite scroll / "Load more" buttons
- Cloudflare or other JS-based bot challenges
- The site needs a logged-in session and uses non-trivial cookies/auth flows

## Minimal Playwright pattern

```python
from playwright.sync_api import sync_playwright

def scrape_dynamic(url: str) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent="my-scraper/1.0")
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")

        # Wait for the content you actually care about
        page.wait_for_selector(".story-card", timeout=10_000)

        items = []
        for card in page.locator(".story-card").all():
            items.append({
                "title": card.locator(".title").inner_text(),
                "url":   card.locator("a").get_attribute("href"),
            })

        browser.close()
        return items
```

## Setup

```bash
pip install playwright
playwright install chromium   # ~150 MB download
```

## Hosting Playwright on GitHub Actions

Add this step before running the script:

```yaml
- name: Install Playwright browsers
  run: |
    pip install playwright
    playwright install --with-deps chromium
```

Plain `requests` workflows run in ~10s. Playwright workflows run in ~45–90s. Plan accordingly if you're scraping many sites.

## Anti-detection (when needed, legally)

- Rotate `User-Agent`
- Use `playwright-stealth` for fingerprint masking
- Throttle: `page.wait_for_timeout(1500)` between requests
- Use residential proxies for high-volume work (Bright Data, Oxylabs)

> **I will not help with:** scraping behind paywalls, copyrighted content, LinkedIn (their ToS is enforced and the hiQ Labs precedent is narrow), or anything that requires defeating active security to access non-public data.

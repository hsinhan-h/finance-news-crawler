"""
Bloomberg scraper.
Bloomberg is heavily protected (paywall + anti-bot). We attempt to scrape
the public-facing homepage markup. Failures are expected and handled gracefully.
"""
from bs4 import BeautifulSoup
from .base import BaseScraper


class BloombergScraper(BaseScraper):
    name = "Bloomberg"
    url = "https://www.bloomberg.com/markets"

    def scrape(self) -> list[dict]:
        resp = self.fetch(self.url, extra_headers={"Referer": "https://www.google.com/"})
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []

        # Bloomberg renders story cards with various class patterns
        selectors = [
            {"name": "a", "attrs": {"data-component": "headline"}},
        ]
        seen = set()

        # Try common link patterns
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "")
            title = tag.get_text(strip=True)
            if not title or len(title) < 20:
                continue
            # Bloomberg article URLs contain /news/ or /articles/
            if not any(seg in href for seg in ["/news/", "/articles/"]):
                continue
            if title in seen:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://www.bloomberg.com{href}"
            articles.append({
                "title": title,
                "url": full_url,
                "summary": "",
            })
            if len(articles) >= self.max_articles:
                break

        return articles

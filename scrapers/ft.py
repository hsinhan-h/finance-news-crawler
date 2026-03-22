"""
Financial Times scraper.
FT has a paywall. We scrape publicly visible article titles from their homepage.
"""
from bs4 import BeautifulSoup
from .base import BaseScraper


class FTScraper(BaseScraper):
    name = "Financial Times"
    url = "https://www.ft.com"

    def scrape(self) -> list[dict]:
        resp = self.fetch(self.url, extra_headers={
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9",
        })
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        seen = set()

        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "")
            title = tag.get_text(strip=True)
            if not title or len(title) < 20:
                continue
            if "/content/" not in href and not href.startswith("/"):
                continue
            if title in seen:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://www.ft.com{href}"
            articles.append({
                "title": title,
                "url": full_url,
                "summary": "",
            })
            if len(articles) >= self.max_articles:
                break

        return articles

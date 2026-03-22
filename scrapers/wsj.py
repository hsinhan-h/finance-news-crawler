"""
Wall Street Journal scraper.
WSJ has a paywall. We scrape publicly visible content from their markets section.
"""
from bs4 import BeautifulSoup
from .base import BaseScraper


class WSJScraper(BaseScraper):
    name = "Wall Street Journal"
    url = "https://www.wsj.com/news/markets"

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
            if "/articles/" not in href:
                continue
            if title in seen:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://www.wsj.com{href}"
            articles.append({
                "title": title,
                "url": full_url,
                "summary": "",
            })
            if len(articles) >= self.max_articles:
                break

        return articles

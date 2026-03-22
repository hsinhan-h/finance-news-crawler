"""工商時報 (ctee.com.tw) scraper."""
from bs4 import BeautifulSoup
from .base import BaseScraper


class CteeScraper(BaseScraper):
    name = "工商時報"
    url = "https://www.ctee.com.tw/"

    def scrape(self) -> list[dict]:
        resp = self.fetch(self.url, extra_headers={
            "Referer": "https://www.google.com/",
        })
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        seen = set()

        # Article links follow pattern /news/YYYYMMDD[id]-[catcode]
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "")
            title = tag.get_text(strip=True)
            if not title or len(title) < 8 or title in seen:
                continue
            if "/news/" not in href:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://www.ctee.com.tw{href}"
            articles.append({"title": title, "url": full_url, "summary": ""})
            if len(articles) >= self.max_articles:
                break

        return articles

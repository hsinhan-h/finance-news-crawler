"""數位時代 (bnext.com.tw) scraper."""
from bs4 import BeautifulSoup
from .base import BaseScraper


class BnextScraper(BaseScraper):
    name = "數位時代"
    url = "https://www.bnext.com.tw/"

    def scrape(self) -> list[dict]:
        resp = self.fetch(self.url, extra_headers={
            "Referer": "https://www.bnext.com.tw/",
        })
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        seen = set()

        for item in soup.select("article a, .post-title a, h2 a, h3 a, .card-title a"):
            href = item.get("href", "")
            title = item.get_text(strip=True)
            if not title or len(title) < 8 or title in seen:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://www.bnext.com.tw{href}"
            parent = item.find_parent(["article", "li", "div"])
            summary = ""
            if parent:
                p = parent.find("p")
                if p:
                    summary = p.get_text(strip=True)[:200]
            articles.append({"title": title, "url": full_url, "summary": summary})
            if len(articles) >= self.max_articles:
                break

        # Fallback generic scan
        if not articles:
            for tag in soup.find_all("a", href=True):
                href = tag.get("href", "")
                title = tag.get_text(strip=True)
                if not title or len(title) < 10 or title in seen:
                    continue
                if "/article/" not in href and "/news/" not in href:
                    continue
                seen.add(title)
                full_url = href if href.startswith("http") else f"https://www.bnext.com.tw{href}"
                articles.append({"title": title, "url": full_url, "summary": ""})
                if len(articles) >= self.max_articles:
                    break

        return articles

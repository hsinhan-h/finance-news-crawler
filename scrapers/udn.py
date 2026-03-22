"""經濟日報 (money.udn.com) scraper."""
from bs4 import BeautifulSoup
from .base import BaseScraper


class UDNScraper(BaseScraper):
    name = "經濟日報"
    url = "https://money.udn.com/money/cate/5591"  # 財經要聞

    def scrape(self) -> list[dict]:
        resp = self.fetch(self.url, extra_headers={
            "Referer": "https://money.udn.com/",
        })
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        seen = set()

        # UDN story list items
        for item in soup.select("h3.story__headline a, h2.story__headline a, .story-list__item a[href*='/story/']"):
            href = item.get("href", "")
            title = item.get_text(strip=True)
            if not title or title in seen:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://money.udn.com{href}"
            # Try to grab summary from sibling paragraph
            parent = item.find_parent(["li", "div", "article"])
            summary = ""
            if parent:
                p = parent.find("p")
                if p:
                    summary = p.get_text(strip=True)[:200]
            articles.append({"title": title, "url": full_url, "summary": summary})
            if len(articles) >= self.max_articles:
                break

        # Fallback: scan all story links
        if not articles:
            for tag in soup.find_all("a", href=True):
                href = tag.get("href", "")
                title = tag.get_text(strip=True)
                if not title or len(title) < 10 or title in seen:
                    continue
                if "/story/" not in href:
                    continue
                seen.add(title)
                full_url = href if href.startswith("http") else f"https://money.udn.com{href}"
                articles.append({"title": title, "url": full_url, "summary": ""})
                if len(articles) >= self.max_articles:
                    break

        return articles

"""MoneyDJ 理財網 (moneydj.com) scraper."""
from bs4 import BeautifulSoup
from .base import BaseScraper


class MoneyDJScraper(BaseScraper):
    name = "MoneyDJ"
    url = "https://www.moneydj.com/KMDJ/News/NewsViewer.aspx?a=mb010000-mb010001"

    def fetch(self, url, extra_headers=None):
        # MoneyDJ has an outdated SSL certificate; bypass verification
        import random, time, requests
        from .base import USER_AGENTS
        headers = self._default_headers()
        if extra_headers:
            headers.update(extra_headers)
        for attempt in range(self.retries):
            try:
                resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                self.logger.warning(f"[{self.name}] Attempt {attempt + 1}/{self.retries} failed: {e}")
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def scrape(self) -> list[dict]:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = self.fetch(self.url, extra_headers={
            "Referer": "https://www.moneydj.com/",
        })
        if not resp:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        seen = set()

        # MoneyDJ news list
        for item in soup.select("a[href*='NewsViewer'], a[href*='/news/']"):
            href = item.get("href", "")
            title = item.get_text(strip=True)
            if not title or len(title) < 8 or title in seen:
                continue
            seen.add(title)
            full_url = href if href.startswith("http") else f"https://www.moneydj.com{href}"
            articles.append({"title": title, "url": full_url, "summary": ""})
            if len(articles) >= self.max_articles:
                break

        # Fallback
        if not articles:
            for tag in soup.select("td a, li a"):
                href = tag.get("href", "")
                title = tag.get_text(strip=True)
                if not title or len(title) < 8 or title in seen:
                    continue
                if not href:
                    continue
                seen.add(title)
                full_url = href if href.startswith("http") else f"https://www.moneydj.com{href}"
                articles.append({"title": title, "url": full_url, "summary": ""})
                if len(articles) >= self.max_articles:
                    break

        return articles

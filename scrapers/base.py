import logging
import random
import time
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

IMPORTANT_KEYWORDS = [
    "央行", "Fed", "升息", "降息", "通膨", "CPI", "GDP",
    "裁員", "倒閉", "IPO", "AI", "半導體", "台積電", "輝達",
    "nvidia", "漲價",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


def is_important(title: str, summary: str = "") -> bool:
    text = (title + " " + summary).lower()
    return any(kw.lower() in text for kw in IMPORTANT_KEYWORDS)


class BaseScraper:
    name: str = "BaseScraper"
    url: str = ""

    def __init__(self, max_articles: int = 10, timeout: int = 30, retries: int = 3):
        self.max_articles = max_articles
        self.timeout = timeout
        self.retries = retries
        self.logger = logging.getLogger(self.name)
        self.session = requests.Session()
        self.session.headers.update(self._default_headers())

    def _default_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def fetch(self, url: str, extra_headers: dict = None) -> requests.Response | None:
        headers = {}
        if extra_headers:
            headers.update(extra_headers)
        for attempt in range(self.retries):
            try:
                resp = self.session.get(url, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                return resp
            except requests.RequestException as e:
                self.logger.warning(f"[{self.name}] Attempt {attempt + 1}/{self.retries} failed for {url}: {e}")
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
        return None

    def parse(self, resp: requests.Response) -> list[dict]:
        raise NotImplementedError

    def scrape(self) -> list[dict]:
        raise NotImplementedError

    def get_articles(self) -> list[dict]:
        try:
            articles = self.scrape()
            for a in articles:
                a.setdefault("summary", "")
                a["is_important"] = is_important(a.get("title", ""), a.get("summary", ""))
            return articles[: self.max_articles]
        except Exception as e:
            self.logger.error(f"[{self.name}] Scraping failed: {e}", exc_info=True)
            return []


class RSSBaseScraper(BaseScraper):
    """For sites that provide RSS feeds — more reliable than HTML scraping."""

    rss_url: str = ""

    def scrape(self) -> list[dict]:
        resp = self.fetch(self.rss_url)
        if not resp:
            return []
        return self._parse_rss(resp.text)

    def _parse_rss(self, xml_text: str) -> list[dict]:
        articles = []
        try:
            root = ET.fromstring(xml_text)
            ns = {}
            channel = root.find("channel")
            if channel is None:
                channel = root
            items = channel.findall("item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            for item in items:
                title = self._get_text(item, ["title"])
                link = self._get_text(item, ["link", "guid"])
                desc = self._get_text(item, ["description", "summary", "content"])
                if not title:
                    continue
                # Strip HTML tags from description
                if desc:
                    soup = BeautifulSoup(desc, "lxml")
                    desc = soup.get_text(separator=" ").strip()
                articles.append({
                    "title": title.strip(),
                    "url": link.strip() if link else "",
                    "summary": (desc or "").strip()[:300],
                })
                if len(articles) >= self.max_articles:
                    break
        except ET.ParseError as e:
            self.logger.error(f"[{self.name}] RSS parse error: {e}")
        return articles

    def _get_text(self, element, tags: list[str]) -> str:
        for tag in tags:
            child = element.find(tag)
            if child is not None:
                if child.text:
                    return child.text
                # Atom <link> uses href attribute
                href = child.get("href")
                if href:
                    return href
        return ""

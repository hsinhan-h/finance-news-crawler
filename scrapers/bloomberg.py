"""
Bloomberg scraper.
Bloomberg blocks direct scraping aggressively, so we rely on Google News RSS
filtered to bloomberg.com as a more reliable public fallback.
"""
from .base import RSSBaseScraper


class BloombergScraper(RSSBaseScraper):
    name = "Bloomberg"
    url = "https://www.bloomberg.com/markets"
    rss_url = "https://news.google.com/rss/search?q=site:bloomberg.com+markets+OR+finance&hl=en-US&gl=US&ceid=US:en"

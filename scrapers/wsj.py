"""
Wall Street Journal scraper.
WSJ requires JavaScript for the public site, so we use Google News RSS
filtered to wsj.com as a more reliable fallback.
"""
from .base import RSSBaseScraper


class WSJScraper(RSSBaseScraper):
    name = "Wall Street Journal"
    url = "https://www.wsj.com/news/markets"
    rss_url = "https://news.google.com/rss/search?q=site:wsj.com+markets+OR+finance&hl=en-US&gl=US&ceid=US:en"

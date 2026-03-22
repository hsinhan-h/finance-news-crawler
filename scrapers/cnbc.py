"""CNBC Finance scraper — uses RSS feed for reliability."""
from .base import RSSBaseScraper


class CNBCScraper(RSSBaseScraper):
    name = "CNBC"
    url = "https://www.cnbc.com/finance"
    rss_url = "https://www.cnbc.com/id/10000664/device/rss/rss.html"

"""
Financial Times scraper.
FT is Cloudflare-protected, so we use Google News RSS filtered to ft.com
instead of scraping the homepage directly.
"""
from .base import RSSBaseScraper


class FTScraper(RSSBaseScraper):
    name = "Financial Times"
    url = "https://www.ft.com"
    rss_url = "https://news.google.com/rss/search?q=site:ft.com+markets+OR+finance&hl=en-US&gl=US&ceid=US:en"

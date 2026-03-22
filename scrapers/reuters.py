"""
Reuters scraper.
Reuters blocks direct scraping. We use Google News RSS filtered to reuters.com
as a reliable fallback that returns Reuters article titles and links.
"""
from .base import RSSBaseScraper


class ReutersScraper(RSSBaseScraper):
    name = "Reuters"
    url = "https://www.reuters.com/finance"
    # Google News RSS for Reuters business/finance articles
    rss_url = "https://news.google.com/rss/search?q=site:reuters.com+finance+OR+markets&hl=en-US&gl=US&ceid=US:en"

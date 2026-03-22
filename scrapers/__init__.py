from .bloomberg import BloombergScraper
from .reuters import ReutersScraper
from .ft import FTScraper
from .wsj import WSJScraper
from .cnbc import CNBCScraper
from .udn import UDNScraper
from .ctee import CteeScraper
from .moneydj import MoneyDJScraper
from .bnext import BnextScraper

INTERNATIONAL_SCRAPERS = [
    BloombergScraper,
    ReutersScraper,
    FTScraper,
    WSJScraper,
    CNBCScraper,
]

TAIWAN_SCRAPERS = [
    UDNScraper,
    CteeScraper,
    MoneyDJScraper,
    BnextScraper,
]

"""
Fetch yesterday's closing prices for tracked symbols using yfinance.
"""
import logging
from datetime import datetime, timedelta

import yfinance as yf

logger = logging.getLogger(__name__)

TARGETS = [
    {"symbol": "^DJI",  "name": "道瓊（^DJI）"},
    {"symbol": "^GSPC", "name": "S&P 500（^GSPC）"},
    {"symbol": "^IXIC", "name": "納斯達克（^IXIC）"},
    {"symbol": "^RUT",  "name": "羅素 2000（^RUT）"},
    {"symbol": "TLT",   "name": "TLT"},
    {"symbol": "TSM",   "name": "台積電 ADR（TSM）"},
]


def _arrow(change: float) -> str:
    if change > 0:
        return "▲"
    elif change < 0:
        return "▼"
    return "─"


def fetch_stock_data() -> tuple[str, list[dict]]:
    """
    Returns (trade_date_str, list of stock rows).
    trade_date_str is the actual trading date of the data (may differ from yesterday
    if yesterday was a weekend/holiday).
    """
    rows = []
    trade_date = None

    for target in TARGETS:
        symbol = target["symbol"]
        try:
            ticker = yf.Ticker(symbol)
            # Fetch last 5 days to handle weekends/holidays
            hist = ticker.history(period="5d")
            if hist.empty:
                logger.warning(f"No data for {symbol}")
                rows.append({
                    "name": target["name"],
                    "close": "N/A",
                    "change": "N/A",
                    "pct": "N/A",
                    "arrow": "─",
                })
                continue

            latest = hist.iloc[-1]
            actual_date = hist.index[-1].date()
            if trade_date is None:
                trade_date = actual_date

            close = latest["Close"]
            prev_close = hist.iloc[-2]["Close"] if len(hist) >= 2 else close
            change = close - prev_close
            pct = (change / prev_close) * 100 if prev_close else 0

            rows.append({
                "name": target["name"],
                "close": f"{close:,.2f}",
                "change": f"{change:+,.2f}",
                "pct": f"{pct:+.2f}%",
                "arrow": _arrow(change),
            })
        except Exception as e:
            logger.error(f"Failed to fetch {symbol}: {e}")
            rows.append({
                "name": target["name"],
                "close": "N/A",
                "change": "N/A",
                "pct": "N/A",
                "arrow": "─",
            })

    date_str = trade_date.strftime("%Y-%m-%d") if trade_date else "N/A"
    return date_str, rows

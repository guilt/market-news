#!/usr/bin/env python3
"""
Web scraping provider - real data without API keys
"""

import re
from typing import Dict, List, Optional

import requests

from ..cache_mixin import CacheMixin
from ..interfaces import IFinancialProvider
from ..market_data import StockData


class ScrapingFinancialProvider(CacheMixin, IFinancialProvider):
    """Scrape real financial data from public websites"""

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        self._default_ttl = 180  # 3 minutes for stock data

    def isAvailable(self) -> bool:
        """Always available - no API key needed"""
        return True

    def getStockPrice(self, symbol: str) -> Optional[StockData]:
        """Get stock price with caching and 429 fallback"""
        return self._cachedCall("getStockPrice", self._fetchStockPrice, symbol)

    def _fetchStockPrice(self, symbol: str) -> Optional[StockData]:
        """Scrape stock price from Yahoo Finance"""
        try:
            # Yahoo Finance quote page
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = self.session.get(url, timeout=10)

            if response.status_code == 429:
                raise Exception("Rate limit 429")
            elif response.status_code != 200:
                return None

            html = response.text

            # Extract price using regex
            priceMatch = re.search(r'"regularMarketPrice":\{"raw":([\d.]+)', html)
            changeMatch = re.search(r'"regularMarketChange":\{"raw":([-\d.]+)', html)
            changePercentMatch = re.search(
                r'"regularMarketChangePercent":\{"raw":([-\d.]+)', html
            )

            if not (priceMatch and changeMatch and changePercentMatch):
                return None

            price = float(priceMatch.group(1))
            change = float(changeMatch.group(1))
            changePercent = float(changePercentMatch.group(1))

            return StockData(
                symbol=symbol,
                price=price,
                change=change,
                changePercent=changePercent,
                explanation="Real-time scraped from Yahoo Finance",
            )

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            return None

    def getMultipleStocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get multiple stocks by scraping individual pages"""
        results = {}
        for symbol in symbols[:5]:  # Limit to avoid being blocked
            data = self.getStockPrice(symbol)
            if data:
                results[symbol] = data
        return results

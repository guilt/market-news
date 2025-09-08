#!/usr/bin/env python3
"""
Google Finance scraping provider - backup for Yahoo
"""

import re
from typing import Dict, List, Optional

import requests

from ..cache_mixin import CacheMixin
from ..interfaces import IFinancialProvider
from ..market_data import StockData


class GoogleFinanceProvider(CacheMixin, IFinancialProvider):
    """Scrape Google Finance for stock data"""

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        self._default_ttl = 180  # 3 minutes

    def isAvailable(self) -> bool:
        """Always available"""
        return True

    def getStockPrice(self, symbol: str) -> Optional[StockData]:
        """Get stock price with caching"""
        return self._cachedCall("getStockPrice", self._fetchStockPrice, symbol)

    def _fetchStockPrice(self, symbol: str) -> Optional[StockData]:
        """Scrape from Google Finance"""
        try:
            # Google Finance URL
            url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
            response = self.session.get(url, timeout=10)

            if response.status_code == 429:
                raise Exception("Rate limit 429")
            elif response.status_code != 200:
                return None

            html = response.text

            # Extract price and change using regex patterns
            priceMatch = re.search(r'data-last-price="([\d,.]+)"', html)
            changeMatch = re.search(
                r'data-last-normal-market-change="([-\d,.]+)"', html
            )

            if not (priceMatch and changeMatch):
                # Try alternative patterns
                priceMatch = re.search(r'"c1":"([\d,.]+)"', html)
                changeMatch = re.search(r'"cp":"([-\d,.]+)"', html)

            if not (priceMatch and changeMatch):
                return None

            price = float(priceMatch.group(1).replace(",", ""))
            changePercent = float(changeMatch.group(1).replace(",", ""))
            change = price * (changePercent / 100)

            return StockData(
                symbol=symbol,
                price=price,
                change=change,
                changePercent=changePercent,
                explanation="Real-time scraped from Google Finance",
            )

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            return None

    def getMultipleStocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get multiple stocks"""
        results = {}
        for symbol in symbols[:3]:  # Conservative limit
            data = self.getStockPrice(symbol)
            if data:
                results[symbol] = data
        return results

#!/usr/bin/env python3
"""
MarketWatch scraping provider - another free source
"""

import re
from typing import Dict, List, Optional

import requests

from ..interfaces import IFinancialProvider
from ..market_data import StockData


class MarketWatchProvider(IFinancialProvider):
    """Scrape MarketWatch for stock data"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        self.cache = {}

    def isAvailable(self) -> bool:
        """Always available"""
        return True

    def getStockPrice(self, symbol: str) -> Optional[StockData]:
        """Scrape from MarketWatch"""
        if symbol in self.cache:
            return self.cache[symbol]

        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                return None

            html = response.text

            # MarketWatch patterns
            priceMatch = re.search(
                r'<bg-quote[^>]*field="Last"[^>]*>([^<]+)</bg-quote>', html
            )
            changeMatch = re.search(
                r'<bg-quote[^>]*field="Change"[^>]*>([^<]+)</bg-quote>', html
            )
            changePercentMatch = re.search(
                r'<bg-quote[^>]*field="PercentChange"[^>]*>([^<]+)</bg-quote>', html
            )

            if not (priceMatch and changeMatch and changePercentMatch):
                return None

            price = float(priceMatch.group(1).replace("$", "").replace(",", ""))
            change = float(changeMatch.group(1).replace("$", "").replace(",", ""))
            changePercent = float(
                changePercentMatch.group(1).replace("%", "").replace(",", "")
            )

            stockData = StockData(
                symbol=symbol,
                price=price,
                change=change,
                changePercent=changePercent,
                explanation="Real-time scraped from MarketWatch",
            )

            self.cache[symbol] = stockData
            return stockData

        except Exception:
            return None

    def getMultipleStocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get multiple stocks"""
        results = {}
        for symbol in symbols[:3]:
            data = self.getStockPrice(symbol)
            if data:
                results[symbol] = data
        return results

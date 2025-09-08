#!/usr/bin/env python3
"""
Yahoo Finance provider (free, no API key required)
"""

from typing import Dict, List, Optional

import requests

from ..cache_mixin import CacheMixin
from ..interfaces import IFinancialProvider
from ..market_data import StockData


class YahooFinanceProvider(CacheMixin, IFinancialProvider):
    """Free financial data from Yahoo Finance"""

    def __init__(self):
        super().__init__()
        self.baseUrl = "https://query1.finance.yahoo.com/v8/finance/chart"
        self._default_ttl = 180  # 3 minutes

    def isAvailable(self) -> bool:
        """Yahoo Finance is always available (no API key required)"""
        return True

    def getStockPrice(self, symbol: str) -> Optional[StockData]:
        """Get stock price with caching"""
        return self._cachedCall("getStockPrice", self._fetchStockPrice, symbol)

    def _fetchStockPrice(self, symbol: str) -> Optional[StockData]:
        """Fetch stock price from Yahoo Finance API"""
        try:
            url = f"{self.baseUrl}/{symbol}"
            params = {"interval": "1d", "range": "1d"}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 429:
                raise Exception("Rate limit 429")
            elif response.status_code != 200:
                return None

            data = response.json()
            result = data.get("chart", {}).get("result", [])

            if not result:
                return None

            quote = result[0]
            meta = quote.get("meta", {})

            currentPrice = meta.get("regularMarketPrice", 0)
            previousClose = meta.get("previousClose", currentPrice)

            change = currentPrice - previousClose
            changePercent = (change / previousClose * 100) if previousClose > 0 else 0

            return StockData(
                symbol=symbol,
                price=float(currentPrice),
                change=float(change),
                changePercent=float(changePercent),
                explanation="Real-time data from Yahoo Finance",
            )

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            return None

    def getMultipleStocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get multiple stocks from Yahoo Finance"""
        return self._cachedCall(
            "getMultipleStocks", self._fetchMultipleStocks, tuple(symbols)
        )

    def _fetchMultipleStocks(self, symbols: tuple) -> Dict[str, StockData]:
        """Fetch multiple stocks"""
        results = {}
        symbolsList = list(symbols)

        # Yahoo supports comma-separated symbols
        try:
            symbolsStr = ",".join(symbolsList)
            url = f"{self.baseUrl}/{symbolsStr}"
            params = {"interval": "1d", "range": "1d"}

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 429:
                raise Exception("Rate limit 429")
            elif response.status_code != 200:
                # Fallback to individual calls
                for symbol in symbolsList:
                    data = self.getStockPrice(symbol)
                    if data:
                        results[symbol] = data
                return results

            data = response.json()
            chartResults = data.get("chart", {}).get("result", [])

            for result in chartResults:
                meta = result.get("meta", {})
                symbol = meta.get("symbol", "")

                if not symbol:
                    continue

                currentPrice = meta.get("regularMarketPrice", 0)
                previousClose = meta.get("previousClose", currentPrice)

                change = currentPrice - previousClose
                changePercent = (
                    (change / previousClose * 100) if previousClose > 0 else 0
                )

                stockData = StockData(
                    symbol=symbol,
                    price=float(currentPrice),
                    change=float(change),
                    changePercent=float(changePercent),
                    explanation="Real-time data from Yahoo Finance",
                )

                results[symbol] = stockData

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            # Fallback to individual calls
            for symbol in symbolsList:
                try:
                    data = self.getStockPrice(symbol)
                    if data:
                        results[symbol] = data
                except Exception:
                    continue

        return results

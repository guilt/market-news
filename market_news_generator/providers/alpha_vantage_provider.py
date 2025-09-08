#!/usr/bin/env python3
"""
Alpha Vantage financial data provider
"""

import os
from typing import Dict, List, Optional

import requests

from ..interfaces import IFinancialProvider
from ..market_data import StockData


class AlphaVantageProvider(IFinancialProvider):
    """Real financial data from Alpha Vantage API"""

    def __init__(self, apiKey: Optional[str] = None):
        self.apiKey = apiKey or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.baseUrl = "https://www.alphavantage.co/query"
        self.cache = {}  # Simple cache to avoid rate limits

    def isAvailable(self) -> bool:
        """Check if API key is available"""
        return self.apiKey is not None

    def getStockPrice(self, symbol: str) -> Optional[StockData]:
        """Get real-time stock price from Alpha Vantage"""
        if not self.isAvailable():
            return None

        # Check cache first
        if symbol in self.cache:
            return self.cache[symbol]

        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.apiKey,
            }

            response = requests.get(self.baseUrl, params=params, timeout=10)
            if response.status_code != 200:
                return None

            data = response.json()
            quote = data.get("Global Quote", {})

            if not quote:
                return None

            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            changePercent = float(quote.get("10. change percent", "0%").rstrip("%"))

            stockData = StockData(
                symbol=symbol,
                price=price,
                change=change,
                changePercent=changePercent,
                explanation="Real-time data from Alpha Vantage",
            )

            # Cache result
            self.cache[symbol] = stockData
            return stockData

        except Exception:
            return None

    def getMultipleStocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get multiple stocks (Alpha Vantage doesn't support batch, so call individually)"""
        results = {}
        for symbol in symbols:
            data = self.getStockPrice(symbol)
            if data:
                results[symbol] = data
        return results

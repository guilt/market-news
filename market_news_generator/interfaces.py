#!/usr/bin/env python3
"""
Core interfaces for data providers - enables real news and financial data integration
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .market_data import NewsItem, StockData


class INewsProvider(ABC):
    """Interface for news data providers"""

    @abstractmethod
    def getMarketNews(self, countryCode: str, symbols: List[str]) -> List[NewsItem]:
        """Get market news for specific country and symbols"""
        pass

    @abstractmethod
    def isAvailable(self) -> bool:
        """Check if provider is available (API key, network, etc.)"""
        pass


class IFinancialProvider(ABC):
    """Interface for financial data providers"""

    @abstractmethod
    def getStockPrice(self, symbol: str) -> Optional[StockData]:
        """Get real-time stock price data"""
        pass

    @abstractmethod
    def getMultipleStocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """Get multiple stock prices efficiently"""
        pass

    @abstractmethod
    def isAvailable(self) -> bool:
        """Check if provider is available"""
        pass


class IMarketDataProvider(ABC):
    """Combined interface for market data"""

    @abstractmethod
    def getStockData(self, symbol: str) -> StockData:
        """Get stock data with fallback"""
        pass

    @abstractmethod
    def getAllStocks(self) -> List[StockData]:
        """Get all tracked stocks"""
        pass

    @abstractmethod
    def getMarketNews(self) -> List[NewsItem]:
        """Get market news with fallback"""
        pass

    @abstractmethod
    def getMarketSummary(self) -> Dict:
        """Get market summary info"""
        pass

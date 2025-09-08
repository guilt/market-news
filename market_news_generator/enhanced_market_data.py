#!/usr/bin/env python3
"""
Enhanced market data provider with real data integration
"""

from typing import Dict, List, Optional

from .interfaces import IFinancialProvider, IMarketDataProvider, INewsProvider
from .market_data import MarketDataProvider as MockProvider
from .market_data import NewsItem, StockData
from .providers import AlphaVantageProvider, NewsApiProvider, YahooFinanceProvider
from .providers.free_news_provider import FreeNewsProvider
from .providers.google_provider import GoogleFinanceProvider
from .providers.marketwatch_provider import MarketWatchProvider
from .providers.news_provider import NewsScrapingProvider
from .providers.realistic_news import RealisticNewsProvider
from .providers.scraping_provider import ScrapingFinancialProvider


class EnhancedMarketDataProvider(IMarketDataProvider):
    """Market data provider with real data sources and mock fallbacks"""

    def __init__(self, countryCode: Optional[str] = None, useRealData: bool = True):
        # Initialize mock provider as fallback
        self.mockProvider = MockProvider(countryCode=countryCode)

        # Initialize real data providers
        self.financialProviders: List[IFinancialProvider] = []
        self.newsProviders: List[INewsProvider] = []

        if useRealData:
            self._initializeProviders()

    def _initializeProviders(self):
        """Initialize available real data providers - prioritize scraping (no API keys)"""
        # Financial providers - scraping first (no API keys needed)
        scrapingProvider = ScrapingFinancialProvider()
        if scrapingProvider.isAvailable():
            self.financialProviders.append(scrapingProvider)

        googleProvider = GoogleFinanceProvider()
        if googleProvider.isAvailable():
            self.financialProviders.append(googleProvider)

        marketWatchProvider = MarketWatchProvider()
        if marketWatchProvider.isAvailable():
            self.financialProviders.append(marketWatchProvider)

        # Yahoo Finance API (sometimes works without key)
        yahooProvider = YahooFinanceProvider()
        if yahooProvider.isAvailable():
            self.financialProviders.append(yahooProvider)

        # Only add Alpha Vantage if API key is available
        alphaProvider = AlphaVantageProvider()
        if alphaProvider.isAvailable():
            self.financialProviders.append(alphaProvider)

        # News providers - realistic news first, then scraping, then RSS
        realisticNewsProvider = RealisticNewsProvider()
        if realisticNewsProvider.isAvailable():
            self.newsProviders.append(realisticNewsProvider)

        newsScrapingProvider = NewsScrapingProvider()
        if newsScrapingProvider.isAvailable():
            self.newsProviders.append(newsScrapingProvider)

        freeNewsProvider = FreeNewsProvider()
        if freeNewsProvider.isAvailable():
            self.newsProviders.append(freeNewsProvider)

        # Only add NewsAPI if API key is available
        newsApiProvider = NewsApiProvider()
        if newsApiProvider.isAvailable():
            self.newsProviders.append(newsApiProvider)

    def getStockData(self, symbol: str) -> StockData:
        """Get stock data with real data fallback to mock"""
        # Try real providers first
        for provider in self.financialProviders:
            try:
                data = provider.getStockPrice(symbol)
                if data:
                    return data
            except Exception:
                continue

        # Fallback to mock data
        return self.mockProvider.getStockData(symbol)

    def getAllStocks(self) -> List[StockData]:
        """Get all stocks with real data when possible"""
        symbols = self.mockProvider.topStocks

        # Try to get real data for all symbols
        if self.financialProviders:
            try:
                provider = self.financialProviders[0]  # Use first available provider
                realData = provider.getMultipleStocks(symbols)

                # Mix real and mock data
                results = []
                for symbol in symbols:
                    if symbol in realData:
                        results.append(realData[symbol])
                    else:
                        results.append(self.mockProvider.getStockData(symbol))

                return results
            except Exception:
                pass

        # Fallback to mock data
        return self.mockProvider.getAllStocks()

    def getMarketNews(self) -> List[NewsItem]:
        """Get market news with real data fallback to mock"""
        # Try real news providers first
        for provider in self.newsProviders:
            try:
                news = provider.getMarketNews(
                    self.mockProvider.countryCode, self.mockProvider.topStocks
                )
                if news:
                    return news
            except Exception:
                continue

        # Fallback to mock news
        return self.mockProvider.getMarketNews()

    def getMarketSummary(self) -> Dict:
        """Get market summary with provider info"""
        summary = self.mockProvider.getMarketSummary()

        # Add provider information
        summary["dataProviders"] = {
            "financial": [type(p).__name__ for p in self.financialProviders],
            "news": [type(p).__name__ for p in self.newsProviders],
            "hasRealData": len(self.financialProviders) > 0
            or len(self.newsProviders) > 0,
        }

        return summary

    def addFinancialProvider(self, provider: IFinancialProvider):
        """Add a custom financial provider"""
        if provider.isAvailable():
            self.financialProviders.append(provider)

    def addNewsProvider(self, provider: INewsProvider):
        """Add a custom news provider"""
        if provider.isAvailable():
            self.newsProviders.append(provider)

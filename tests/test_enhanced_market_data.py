#!/usr/bin/env python3
"""
Tests for enhanced market data provider
"""

import unittest
from unittest.mock import patch

from market_news_generator.enhanced_market_data import EnhancedMarketDataProvider
from market_news_generator.interfaces import IFinancialProvider, INewsProvider
from market_news_generator.market_data import NewsItem, StockData


class MockFinancialProvider(IFinancialProvider):
    def __init__(self, available=True, returnData=True):
        self.available = available
        self.returnData = returnData

    def isAvailable(self):
        return self.available

    def getStockPrice(self, symbol):
        if self.returnData:
            return StockData(symbol, 100.0, 1.0, 1.0, "Mock data")
        return None

    def getMultipleStocks(self, symbols):
        if self.returnData:
            return {symbol: self.getStockPrice(symbol) for symbol in symbols}
        return {}


class MockNewsProvider(INewsProvider):
    def __init__(self, available=True, returnData=True):
        self.available = available
        self.returnData = returnData

    def isAvailable(self):
        return self.available

    def getMarketNews(self, countryCode, symbols):
        if self.returnData:
            return [NewsItem("Mock headline", "Mock explanation", {"AAPL": "up"})]
        return []


class TestEnhancedMarketDataProvider(unittest.TestCase):
    def setUp(self):
        self.provider = EnhancedMarketDataProvider(useRealData=False)

    def testInitializationWithRealData(self):
        """Test provider initialization with real data enabled"""
        provider = EnhancedMarketDataProvider(useRealData=True)

        # Should have some providers initialized
        self.assertIsInstance(provider.financialProviders, list)
        self.assertIsInstance(provider.newsProviders, list)

    def testInitializationWithoutRealData(self):
        """Test provider initialization with real data disabled"""
        provider = EnhancedMarketDataProvider(useRealData=False)

        # Should have empty provider lists
        self.assertEqual(len(provider.financialProviders), 0)
        self.assertEqual(len(provider.newsProviders), 0)

    def testGetStockDataWithRealProvider(self):
        """Test getting stock data with real provider available"""
        mockProvider = MockFinancialProvider(available=True, returnData=True)
        self.provider.addFinancialProvider(mockProvider)

        stock = self.provider.getStockData("AAPL")

        self.assertIsInstance(stock, StockData)
        self.assertEqual(stock.symbol, "AAPL")
        self.assertEqual(stock.explanation, "Mock data")

    def testGetStockDataFallbackToMock(self):
        """Test fallback to mock data when real providers fail"""
        mockProvider = MockFinancialProvider(available=True, returnData=False)
        self.provider.addFinancialProvider(mockProvider)

        stock = self.provider.getStockData("AAPL")

        self.assertIsInstance(stock, StockData)
        self.assertEqual(stock.symbol, "AAPL")
        # Should be mock data from fallback
        self.assertIn("Apple", stock.explanation)

    def testGetAllStocksWithRealProvider(self):
        """Test getting all stocks with real provider"""
        mockProvider = MockFinancialProvider(available=True, returnData=True)
        self.provider.addFinancialProvider(mockProvider)

        stocks = self.provider.getAllStocks()

        self.assertIsInstance(stocks, list)
        self.assertGreater(len(stocks), 0)

        # Should have real data
        for stock in stocks:
            self.assertEqual(stock.explanation, "Mock data")

    def testGetAllStocksMixedRealMock(self):
        """Test getting stocks with partial real data"""

        # Mock provider that only returns data for some symbols
        class PartialMockProvider(IFinancialProvider):
            def isAvailable(self):
                return True

            def getStockPrice(self, symbol):
                if symbol == "AAPL":
                    return StockData(symbol, 100.0, 1.0, 1.0, "Real data")
                return None

            def getMultipleStocks(self, symbols):
                return {"AAPL": self.getStockPrice("AAPL")}

        self.provider.addFinancialProvider(PartialMockProvider())
        stocks = self.provider.getAllStocks()

        # Should have mix of real and mock data
        realDataCount = sum(1 for stock in stocks if "Real data" in stock.explanation)
        mockDataCount = sum(
            1 for stock in stocks if "Real data" not in stock.explanation
        )

        self.assertGreater(realDataCount, 0)
        self.assertGreater(mockDataCount, 0)

    def testGetMarketNewsWithRealProvider(self):
        """Test getting news with real provider"""
        mockProvider = MockNewsProvider(available=True, returnData=True)
        self.provider.addNewsProvider(mockProvider)

        news = self.provider.getMarketNews()

        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        self.assertEqual(news[0].headline, "Mock headline")

    def testGetMarketNewsFallbackToMock(self):
        """Test fallback to mock news when real providers fail"""
        mockProvider = MockNewsProvider(available=True, returnData=False)
        self.provider.addNewsProvider(mockProvider)

        news = self.provider.getMarketNews()

        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        # Should be mock news from fallback
        self.assertNotEqual(news[0].headline, "Mock headline")

    def testGetMarketSummaryWithProviders(self):
        """Test market summary includes provider information"""
        mockFinancial = MockFinancialProvider()
        mockNews = MockNewsProvider()

        self.provider.addFinancialProvider(mockFinancial)
        self.provider.addNewsProvider(mockNews)

        summary = self.provider.getMarketSummary()

        self.assertIn("dataProviders", summary)
        providers = summary["dataProviders"]

        self.assertIn("financial", providers)
        self.assertIn("news", providers)
        self.assertIn("hasRealData", providers)

        self.assertTrue(providers["hasRealData"])
        self.assertIn("MockFinancialProvider", providers["financial"])
        self.assertIn("MockNewsProvider", providers["news"])

    def testAddFinancialProviderAvailable(self):
        """Test adding available financial provider"""
        mockProvider = MockFinancialProvider(available=True)
        initialCount = len(self.provider.financialProviders)

        self.provider.addFinancialProvider(mockProvider)

        self.assertEqual(len(self.provider.financialProviders), initialCount + 1)

    def testAddFinancialProviderUnavailable(self):
        """Test adding unavailable financial provider"""
        mockProvider = MockFinancialProvider(available=False)
        initialCount = len(self.provider.financialProviders)

        self.provider.addFinancialProvider(mockProvider)

        # Should not be added if unavailable
        self.assertEqual(len(self.provider.financialProviders), initialCount)

    def testAddNewsProviderAvailable(self):
        """Test adding available news provider"""
        mockProvider = MockNewsProvider(available=True)
        initialCount = len(self.provider.newsProviders)

        self.provider.addNewsProvider(mockProvider)

        self.assertEqual(len(self.provider.newsProviders), initialCount + 1)

    def testAddNewsProviderUnavailable(self):
        """Test adding unavailable news provider"""
        mockProvider = MockNewsProvider(available=False)
        initialCount = len(self.provider.newsProviders)

        self.provider.addNewsProvider(mockProvider)

        # Should not be added if unavailable
        self.assertEqual(len(self.provider.newsProviders), initialCount)

    @patch("market_news_generator.enhanced_market_data.YahooFinanceProvider")
    @patch("market_news_generator.enhanced_market_data.ScrapingFinancialProvider")
    def testInitializeProviders(self, mockScraping, mockYahoo):
        """Test provider initialization"""
        # Mock providers as available
        mockScraping.return_value.isAvailable.return_value = True
        mockYahoo.return_value.isAvailable.return_value = True

        provider = EnhancedMarketDataProvider(useRealData=True)

        # Should have initialized providers
        self.assertGreater(len(provider.financialProviders), 0)


if __name__ == "__main__":
    unittest.main()

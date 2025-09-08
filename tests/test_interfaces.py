#!/usr/bin/env python3
"""
Tests for core interfaces
"""

import unittest

from market_news_generator.interfaces import (
    IFinancialProvider,
    IMarketDataProvider,
    INewsProvider,
)
from market_news_generator.market_data import NewsItem, StockData


class MockNewsProvider(INewsProvider):
    """Mock implementation for testing"""

    def __init__(self, available=True):
        self._available = available

    def getMarketNews(self, countryCode, symbols):
        return [NewsItem("Test headline", "Test explanation", {"AAPL": "up"})]

    def isAvailable(self):
        return self._available


class MockFinancialProvider(IFinancialProvider):
    """Mock implementation for testing"""

    def __init__(self, available=True):
        self._available = available

    def getStockPrice(self, symbol):
        if not self._available:
            return None
        return StockData(symbol, 100.0, 1.0, 1.0, "Test stock")

    def getMultipleStocks(self, symbols):
        if not self._available:
            return {}
        return {symbol: self.getStockPrice(symbol) for symbol in symbols}

    def isAvailable(self):
        return self._available


class MockMarketDataProvider(IMarketDataProvider):
    """Mock implementation for testing"""

    def getStockData(self, symbol):
        return StockData(symbol, 100.0, 1.0, 1.0, "Test stock")

    def getAllStocks(self):
        return [self.getStockData("AAPL"), self.getStockData("MSFT")]

    def getMarketNews(self):
        return [NewsItem("Test headline", "Test explanation", {"AAPL": "up"})]

    def getMarketSummary(self):
        return {"country": "US", "currency": "USD"}


class TestINewsProvider(unittest.TestCase):

    def setUp(self):
        self.provider = MockNewsProvider()

    def testGetMarketNews(self):
        """Test news provider interface"""
        news = self.provider.getMarketNews("US", ["AAPL"])

        self.assertIsInstance(news, list)
        self.assertEqual(len(news), 1)
        self.assertIsInstance(news[0], NewsItem)
        self.assertEqual(news[0].headline, "Test headline")

    def testIsAvailable(self):
        """Test availability check"""
        self.assertTrue(self.provider.isAvailable())

        unavailableProvider = MockNewsProvider(available=False)
        self.assertFalse(unavailableProvider.isAvailable())

    def testInterfaceContract(self):
        """Test that interface methods exist"""
        self.assertTrue(hasattr(self.provider, "getMarketNews"))
        self.assertTrue(hasattr(self.provider, "isAvailable"))
        self.assertTrue(callable(self.provider.getMarketNews))
        self.assertTrue(callable(self.provider.isAvailable))


class TestIFinancialProvider(unittest.TestCase):

    def setUp(self):
        self.provider = MockFinancialProvider()

    def testGetStockPrice(self):
        """Test stock price interface"""
        stock = self.provider.getStockPrice("AAPL")

        self.assertIsInstance(stock, StockData)
        self.assertEqual(stock.symbol, "AAPL")
        self.assertEqual(stock.price, 100.0)

    def testGetMultipleStocks(self):
        """Test multiple stocks interface"""
        stocks = self.provider.getMultipleStocks(["AAPL", "MSFT"])

        self.assertIsInstance(stocks, dict)
        self.assertEqual(len(stocks), 2)
        self.assertIn("AAPL", stocks)
        self.assertIn("MSFT", stocks)
        self.assertIsInstance(stocks["AAPL"], StockData)

    def testIsAvailable(self):
        """Test availability check"""
        self.assertTrue(self.provider.isAvailable())

        unavailableProvider = MockFinancialProvider(available=False)
        self.assertFalse(unavailableProvider.isAvailable())

    def testUnavailableProvider(self):
        """Test behavior when provider is unavailable"""
        unavailableProvider = MockFinancialProvider(available=False)

        stock = unavailableProvider.getStockPrice("AAPL")
        self.assertIsNone(stock)

        stocks = unavailableProvider.getMultipleStocks(["AAPL"])
        self.assertEqual(stocks, {})

    def testInterfaceContract(self):
        """Test that interface methods exist"""
        self.assertTrue(hasattr(self.provider, "getStockPrice"))
        self.assertTrue(hasattr(self.provider, "getMultipleStocks"))
        self.assertTrue(hasattr(self.provider, "isAvailable"))


class TestIMarketDataProvider(unittest.TestCase):

    def setUp(self):
        self.provider = MockMarketDataProvider()

    def testGetStockData(self):
        """Test stock data interface"""
        stock = self.provider.getStockData("AAPL")

        self.assertIsInstance(stock, StockData)
        self.assertEqual(stock.symbol, "AAPL")

    def testGetAllStocks(self):
        """Test get all stocks interface"""
        stocks = self.provider.getAllStocks()

        self.assertIsInstance(stocks, list)
        self.assertEqual(len(stocks), 2)
        self.assertIsInstance(stocks[0], StockData)

    def testGetMarketNews(self):
        """Test market news interface"""
        news = self.provider.getMarketNews()

        self.assertIsInstance(news, list)
        self.assertEqual(len(news), 1)
        self.assertIsInstance(news[0], NewsItem)

    def testGetMarketSummary(self):
        """Test market summary interface"""
        summary = self.provider.getMarketSummary()

        self.assertIsInstance(summary, dict)
        self.assertIn("country", summary)
        self.assertIn("currency", summary)

    def testInterfaceContract(self):
        """Test that interface methods exist"""
        self.assertTrue(hasattr(self.provider, "getStockData"))
        self.assertTrue(hasattr(self.provider, "getAllStocks"))
        self.assertTrue(hasattr(self.provider, "getMarketNews"))
        self.assertTrue(hasattr(self.provider, "getMarketSummary"))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Tests for scraping provider with caching
"""

import unittest
from unittest.mock import Mock, patch

from market_news_generator.providers.scraping_provider import ScrapingFinancialProvider


class TestScrapingFinancialProvider(unittest.TestCase):
    def setUp(self):
        self.provider = ScrapingFinancialProvider()
        self.provider._default_ttl = 1  # 1 second for testing

    def testIsAvailable(self):
        """Test provider availability"""
        self.assertTrue(self.provider.isAvailable())

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testFetchStockPriceSuccess(self, mockGet):
        """Test successful stock price fetching"""
        mockResponse = Mock()
        mockResponse.status_code = 200
        mockResponse.text = """
        "regularMarketPrice":{"raw":150.25}
        "regularMarketChange":{"raw":2.50}
        "regularMarketChangePercent":{"raw":1.69}
        """
        mockGet.return_value = mockResponse

        stock = self.provider._fetchStockPrice("AAPL")

        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, "AAPL")
        self.assertEqual(stock.price, 150.25)
        self.assertEqual(stock.change, 2.50)
        self.assertEqual(stock.changePercent, 1.69)

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testFetchStockPrice429Error(self, mockGet):
        """Test 429 rate limit error handling"""
        mockResponse = Mock()
        mockResponse.status_code = 429
        mockGet.return_value = mockResponse

        with self.assertRaises(Exception) as context:
            self.provider._fetchStockPrice("AAPL")

        self.assertIn("429", str(context.exception))

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testFetchStockPrice404Error(self, mockGet):
        """Test 404 error handling"""
        mockResponse = Mock()
        mockResponse.status_code = 404
        mockGet.return_value = mockResponse

        stock = self.provider._fetchStockPrice("INVALID")
        self.assertIsNone(stock)

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testFetchStockPriceInvalidData(self, mockGet):
        """Test handling of invalid response data"""
        mockResponse = Mock()
        mockResponse.status_code = 200
        mockResponse.text = "invalid json data"
        mockGet.return_value = mockResponse

        stock = self.provider._fetchStockPrice("AAPL")
        self.assertIsNone(stock)

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testGetStockPriceWithCaching(self, mockGet):
        """Test stock price retrieval with caching"""
        mockResponse = Mock()
        mockResponse.status_code = 200
        mockResponse.text = """
        "regularMarketPrice":{"raw":150.25}
        "regularMarketChange":{"raw":2.50}
        "regularMarketChangePercent":{"raw":1.69}
        """
        mockGet.return_value = mockResponse

        # First call should fetch from network
        stock1 = self.provider.getStockPrice("AAPL")
        self.assertIsNotNone(stock1)
        self.assertEqual(mockGet.call_count, 1)

        # Second call should use cache
        stock2 = self.provider.getStockPrice("AAPL")
        self.assertIsNotNone(stock2)
        self.assertEqual(mockGet.call_count, 1)  # No additional network call

        # Data should be identical
        self.assertEqual(stock1.price, stock2.price)

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testGetStockPrice429FallbackToCache(self, mockGet):
        """Test 429 error fallback to cached data"""
        # First, populate cache with successful response
        mockResponse = Mock()
        mockResponse.status_code = 200
        mockResponse.text = """
        "regularMarketPrice":{"raw":150.25}
        "regularMarketChange":{"raw":2.50}
        "regularMarketChangePercent":{"raw":1.69}
        """
        mockGet.return_value = mockResponse

        stock1 = self.provider.getStockPrice("AAPL")
        self.assertIsNotNone(stock1)

        # Clear cache to simulate expiry
        import time

        time.sleep(1.1)  # Wait for cache to expire

        # Now return 429 error
        mockResponse.status_code = 429
        mockGet.return_value = mockResponse

        # Should return cached data despite 429 error
        stock2 = self.provider.getStockPrice("AAPL")
        self.assertIsNotNone(stock2)
        self.assertEqual(stock1.price, stock2.price)

    def testGetMultipleStocks(self):
        """Test getting multiple stocks"""
        with patch.object(self.provider, "getStockPrice") as mockGet_stock:
            mockGet_stock.return_value = Mock(symbol="TEST")

            symbols = ["AAPL", "MSFT", "GOOGL"]
            results = self.provider.getMultipleStocks(symbols)

            self.assertEqual(len(results), 3)
            self.assertEqual(mockGet_stock.call_count, 3)

    def testGetMultipleStocksWithFailures(self):
        """Test getting multiple stocks with some failures"""

        def mockGet_stock(symbol):
            if symbol == "AAPL":
                return Mock(symbol="AAPL")
            return None

        with patch.object(self.provider, "getStockPrice", side_effect=mockGet_stock):
            symbols = ["AAPL", "INVALID", "MSFT"]
            results = self.provider.getMultipleStocks(symbols)

            self.assertEqual(len(results), 1)
            self.assertIn("AAPL", results)

    @patch("market_news_generator.providers.scraping_provider.requests.Session.get")
    def testNetworkTimeoutHandling(self, mockGet):
        """Test network timeout handling"""
        mockGet.side_effect = Exception("Connection timeout")

        stock = self.provider._fetchStockPrice("AAPL")
        self.assertIsNone(stock)

    def testCacheKeyConsistency(self):
        """Test that cache keys are consistent for same parameters"""
        key1 = self.provider._getCacheKey("getStockPrice", "AAPL")
        key2 = self.provider._getCacheKey("getStockPrice", "AAPL")
        key3 = self.provider._getCacheKey("getStockPrice", "MSFT")

        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)


if __name__ == "__main__":
    unittest.main()

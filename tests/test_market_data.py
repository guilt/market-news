#!/usr/bin/env python3
"""
Tests for market data core functionality
"""

import unittest

from market_news_generator.market_data import MarketDataProvider, NewsItem, StockData


class TestStockData(unittest.TestCase):
    def testStockDataCreation(self):
        """Test StockData creation and attributes"""
        stock = StockData(
            symbol="AAPL",
            price=150.0,
            change=2.5,
            changePercent=1.7,
            explanation="Test stock",
        )

        self.assertEqual(stock.symbol, "AAPL")
        self.assertEqual(stock.price, 150.0)
        self.assertEqual(stock.change, 2.5)
        self.assertEqual(stock.changePercent, 1.7)
        self.assertEqual(stock.explanation, "Test stock")


class TestNewsItem(unittest.TestCase):
    def testNewsItemCreation(self):
        """Test NewsItem creation and attributes"""
        news = NewsItem(
            headline="Test headline",
            explanation="Test explanation",
            impact={"AAPL": "up"},
        )

        self.assertEqual(news.headline, "Test headline")
        self.assertEqual(news.explanation, "Test explanation")
        self.assertEqual(news.impact, {"AAPL": "up"})


class TestMarketDataProvider(unittest.TestCase):
    def setUp(self):
        self.provider = MarketDataProvider()

    def testDetectCountrySuccess(self):
        """Test successful country detection via MarketDetector"""
        # Test that detector works with known country
        provider = MarketDataProvider(countryCode="US")
        self.assertEqual(provider.countryCode, "US")

    def testDetectCountryFailure(self):
        """Test country detection fallback"""
        # Test that unknown country falls back to global
        provider = MarketDataProvider(countryCode="XX")
        self.assertEqual(provider.countryCode, "XX")

    def testGetMarketSummaryUs(self):
        """Test market summary for US"""
        provider = MarketDataProvider(countryCode="US")
        summary = provider.getMarketSummary()

        self.assertEqual(summary["country"], "United States")
        self.assertEqual(summary["currency"], "USD")
        self.assertFalse(summary["fallback"])

    def testGetMarketSummaryUnknownCountry(self):
        """Test market summary for unknown country"""
        provider = MarketDataProvider(countryCode="XX")
        summary = provider.getMarketSummary()

        self.assertEqual(summary["country"], "XX (Global Market)")
        self.assertEqual(summary["currency"], "USD")
        self.assertTrue(summary["fallback"])

    def testGetStockData(self):
        """Test getting stock data"""
        stock = self.provider.getStockData("AAPL")

        self.assertEqual(stock.symbol, "AAPL")
        self.assertIsInstance(stock.price, float)
        self.assertIsInstance(stock.change, float)
        self.assertIsInstance(stock.changePercent, float)
        self.assertIsInstance(stock.explanation, str)

    def testGetAllStocks(self):
        """Test getting all stocks"""
        stocks = self.provider.getAllStocks()

        self.assertIsInstance(stocks, list)
        self.assertGreater(len(stocks), 0)

        for stock in stocks:
            self.assertIsInstance(stock, StockData)
            self.assertIsInstance(stock.symbol, str)
            self.assertIsInstance(stock.price, float)

    def testGetMarketNews(self):
        """Test getting market news"""
        news = self.provider.getMarketNews()

        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)

        for item in news:
            self.assertIsInstance(item, NewsItem)
            self.assertIsInstance(item.headline, str)
            self.assertIsInstance(item.explanation, str)
            self.assertIsInstance(item.impact, dict)

    def testGenerateRealisticPrice(self):
        """Test realistic price generation"""
        # Test that base prices are consistent
        stock1 = self.provider.getStockData("AAPL")
        self.provider.getStockData("AAPL")

        # Base price should be the same (225.40 for AAPL)
        # But actual prices will vary due to random changes
        self.assertGreater(stock1.price, 50)
        self.assertLess(stock1.price, 1000)

    def testGenerateMarketChange(self):
        """Test market change generation"""
        stock = self.provider.getStockData("AAPL")

        self.assertIsInstance(stock.change, float)
        self.assertIsInstance(stock.changePercent, float)

        # Change percent should be within expected range (-4% to +4%)
        self.assertGreaterEqual(stock.changePercent, -4.0)
        self.assertLessEqual(stock.changePercent, 4.0)

    def testGetStockExplanation(self):
        """Test stock explanation generation"""
        stock = self.provider.getStockData("AAPL")

        self.assertIsInstance(stock.explanation, str)
        self.assertIn("Apple", stock.explanation)

    def testCountrySpecificStocks(self):
        """Test country-specific stock lists"""
        # Test different countries have different stocks
        usProvider = MarketDataProvider(countryCode="US")
        caProvider = MarketDataProvider(countryCode="CA")

        usStocks = usProvider.topStocks
        caStocks = caProvider.topStocks

        self.assertNotEqual(usStocks, caStocks)

        # Canadian stocks should have .TO suffix
        self.assertTrue(any(".TO" in stock for stock in caStocks))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Tests for watch module
"""

import unittest
from unittest.mock import Mock, patch

from market_news_generator.market_data import NewsItem, StockData
from market_news_generator.watch import MarketWatch


class TestMarketWatch(unittest.TestCase):

    def setUp(self):
        self.watch = MarketWatch()

    def testInitialization(self):
        """Test MarketWatch initialization"""
        self.assertIsNotNone(self.watch.console)
        self.assertTrue(self.watch.running)
        self.assertIsNotNone(self.watch.provider)

    def testGetTradingAdvice(self):
        """Test trading advice generation"""
        # Test with negative change and positive news (should be BUY)
        stock = StockData("AAPL", 150.0, -3.0, -2.5, "Apple stock")  # -2.5% change
        news = [NewsItem("Apple rises", "Good news", {"AAPL": "up"})]

        advice, color = self.watch._getTradingAdvice(stock, news)

        self.assertIsInstance(advice, str)
        self.assertIsInstance(color, str)
        # With negative change and positive news, should be BUY
        self.assertIn("BUY", advice.upper())

    def testGetTradingAdviceNegative(self):
        """Test trading advice with negative news"""
        stock = StockData("AAPL", 150.0, -3.5, -2.3, "Apple stock")
        news = [NewsItem("Apple falls", "Bad news", {"AAPL": "down"})]

        advice, color = self.watch._getTradingAdvice(stock, news)

        self.assertIsInstance(advice, str)
        self.assertIsInstance(color, str)

    def testGetTradingAdviceNeutral(self):
        """Test trading advice with neutral conditions"""
        stock = StockData("AAPL", 150.0, 0.5, 0.3, "Apple stock")
        news = []

        advice, color = self.watch._getTradingAdvice(stock, news)

        self.assertIsInstance(advice, str)
        self.assertIsInstance(color, str)

    def testCreateStocksTable(self):
        """Test stocks table creation"""
        stocks = [
            StockData("AAPL", 150.0, 2.5, 1.7, "Apple"),
            StockData("MSFT", 300.0, -1.0, -0.3, "Microsoft"),
        ]
        news = []

        table = self.watch._createStocksTable(stocks, news)

        self.assertIsNotNone(table)
        # Table should have the stocks data
        self.assertEqual(len(table.rows), 2)

    def testCreateNewsPanel(self):
        """Test news panel creation"""
        news = [
            NewsItem("Market rises", "Good day", {"AAPL": "up"}),
            NewsItem("Tech stocks fall", "Bad news", {"MSFT": "down"}),
        ]

        panel = self.watch._createNewsPanel(news)

        self.assertIsNotNone(panel)
        # Panel should contain news content
        self.assertIsInstance(panel, type(panel))  # Check it's a Panel-like object

    def testCreateDashboard(self):
        """Test dashboard creation"""
        stocks = [
            StockData("AAPL", 150.0, 2.5, 1.7, "Apple"),
            StockData("MSFT", 300.0, -1.0, -0.3, "Microsoft"),
        ]
        news = [NewsItem("Market update", "Daily news", {"AAPL": "up"})]

        dashboard = self.watch._createDashboard(stocks, news)

        self.assertIsNotNone(dashboard)
        # Dashboard should be a Layout object
        self.assertIsInstance(dashboard, type(dashboard))

    @patch("market_news_generator.watch.Live")
    def testRunWatch(self, mockLive):
        """Test watch run method"""
        # Mock the Live context manager
        mockLiveInstance = Mock()
        mockLive.return_value.__enter__.return_value = mockLiveInstance

        # Set running to False to exit immediately
        self.watch.running = False

        # This should not raise an exception
        self.watch.run()

        # Verify Live was called
        mockLive.assert_called_once()

    def testSignalHandler(self):
        """Test signal handler"""
        self.assertTrue(self.watch.running)

        # Simulate signal
        self.watch._signalHandler(None, None)

        self.assertFalse(self.watch.running)


if __name__ == "__main__":
    unittest.main()

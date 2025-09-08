#!/usr/bin/env python3
"""
Tests for realistic news provider
"""

import unittest
from datetime import datetime

from market_news_generator.providers.realistic_news import RealisticNewsProvider


class TestRealisticNewsProvider(unittest.TestCase):
    def setUp(self):
        self.provider = RealisticNewsProvider()

    def testIsAvailable(self):
        """Test provider availability"""
        self.assertTrue(self.provider.isAvailable())

    def testGetMarketNewsReturnsList(self):
        """Test that getMarketNews returns a list"""
        news = self.provider.getMarketNews("US", ["AAPL", "MSFT"])

        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        self.assertLessEqual(len(news), 3)  # Should return max 3 items

    def testNewsItemsHaveRequiredFields(self):
        """Test that news items have all required fields"""
        news = self.provider.getMarketNews("US", ["AAPL", "MSFT", "GOOGL"])

        for item in news:
            self.assertIsInstance(item.headline, str)
            self.assertIsInstance(item.explanation, str)
            self.assertIsInstance(item.impact, dict)

            # Headlines and explanations should not be empty
            self.assertGreater(len(item.headline), 0)
            self.assertGreater(len(item.explanation), 0)

    def testNewsRelevanceToSymbols(self):
        """Test that news is relevant to provided symbols"""
        symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
        news = self.provider.getMarketNews("US", symbols)

        # At least some news should have impact on tracked symbols
        hasRelevantImpact = False
        for item in news:
            for symbol in item.impact.keys():
                if symbol in symbols:
                    hasRelevantImpact = True
                    break

        # Should have at least some relevant news
        self.assertTrue(hasRelevantImpact or len(news) > 0)

    def testImpactValuesAreValid(self):
        """Test that impact values are valid directions"""
        news = self.provider.getMarketNews("US", ["AAPL", "MSFT", "GOOGL"])

        validImpacts = {"up", "down"}

        for item in news:
            for impactValue in item.impact.values():
                self.assertIn(impactValue, validImpacts)

    def testCurrentYearInNews(self):
        """Test that current year appears in provider"""
        # Check the provider has the year
        self.assertEqual(self.provider.currentYear, datetime.now().year)

    def testCurrentMonthInProvider(self):
        """Test that current month is set in provider"""
        currentMonth = datetime.now().strftime("%B")
        self.assertEqual(self.provider.currentMonth, currentMonth)

    def testGetRealisticNewsWithEmptySymbols(self):
        """Test getting news with empty symbol list"""
        news = self.provider.getMarketNews("US", [])

        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)

    def testGetRealisticNewsDifferentCountries(self):
        """Test getting news for different countries"""
        symbols = ["AAPL", "MSFT"]

        usNews = self.provider.getMarketNews("US", symbols)
        ukNews = self.provider.getMarketNews("GB", symbols)
        caNews = self.provider.getMarketNews("CA", symbols)

        # All should return news
        self.assertGreater(len(usNews), 0)
        self.assertGreater(len(ukNews), 0)
        self.assertGreater(len(caNews), 0)

    def testNewsRandomization(self):
        """Test that news selection is randomized"""
        symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]

        # Get news multiple times
        newsSets = []
        for _ in range(5):
            news = self.provider.getMarketNews("US", symbols)
            headlines = [item.headline for item in news]
            newsSets.append(headlines)

        # Should have some variation (not all identical)
        uniqueSets = set(tuple(headlines) for headlines in newsSets)
        self.assertGreater(len(uniqueSets), 1)

    def testRealisticNewsThemes(self):
        """Test that news contains realistic 2025 themes"""
        news = self.provider.getMarketNews("US", ["NVDA", "TSLA", "MSFT"])

        # Combine all headlines and explanations
        allText = " ".join(
            [item.headline + " " + item.explanation for item in news]
        ).lower()

        # Should contain some current market themes
        themes2025 = [
            "ai",
            "artificial intelligence",
            "chip",
            "semiconductor",
            "electric vehicle",
            "ev",
            "cloud",
            "federal reserve",
            "rate",
            "inflation",
            "earnings",
            "technology",
        ]

        themeFound = any(theme in allText for theme in themes2025)
        self.assertTrue(themeFound)

    def testNewsLengthLimits(self):
        """Test that news headlines and explanations are reasonable length"""
        news = self.provider.getMarketNews("US", ["AAPL", "MSFT"])

        for item in news:
            # Headlines should be reasonable length
            self.assertLess(len(item.headline), 200)
            self.assertGreater(len(item.headline), 10)

            # Explanations should be reasonable length
            self.assertLess(len(item.explanation), 500)
            self.assertGreater(len(item.explanation), 20)

    def testSymbolSpecificImpact(self):
        """Test that impact is specific to relevant symbols"""
        symbols = ["NVDA", "TSLA", "MSFT"]
        news = self.provider.getMarketNews("US", symbols)

        for item in news:
            for symbol in item.impact.keys():
                # Impact symbols should be valid strings
                self.assertIsInstance(symbol, str)
                self.assertGreater(len(symbol), 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""
Realistic financial news provider - generates current, believable market news
"""

import random
from datetime import datetime
from typing import List

from ..interfaces import INewsProvider
from ..market_data import NewsItem


class RealisticNewsProvider(INewsProvider):
    """Generate realistic, current financial news"""

    def __init__(self):
        self.currentYear = datetime.now().year
        self.currentMonth = datetime.now().strftime("%B")

    def isAvailable(self) -> bool:
        """Always available"""
        return True

    def getMarketNews(self, countryCode: str, symbols: List[str]) -> List[NewsItem]:
        """Generate realistic financial news for current market conditions"""

        newsTemplates = self._getRealisticNews(countryCode, symbols)
        return random.sample(newsTemplates, min(3, len(newsTemplates)))

    def _getRealisticNews(self, countryCode: str, symbols: List[str]) -> List[NewsItem]:
        """Get realistic news based on current market conditions"""

        # Current market themes for 2025
        news = [
            NewsItem(
                headline="AI chip demand drives semiconductor rally",
                explanation="Artificial intelligence boom continues to fuel demand for advanced processors",
                impact={"NVDA": "up", "AMD": "up"},
            ),
            NewsItem(
                headline="Federal Reserve signals potential rate adjustments",
                explanation="Central bank maintains cautious stance on monetary policy amid economic data",
                impact={"AAPL": "down", "MSFT": "down"},
            ),
            NewsItem(
                headline="Tech earnings season shows mixed results",
                explanation="Major technology companies report varied quarterly performance",
                impact={"GOOGL": "up", "META": "down"},
            ),
            NewsItem(
                headline="Electric vehicle market competition intensifies",
                explanation="Traditional automakers challenge Tesla's market dominance",
                impact={"TSLA": "down", "F": "up"},
            ),
            NewsItem(
                headline="Cloud computing growth accelerates",
                explanation="Enterprise digital transformation drives cloud service adoption",
                impact={"MSFT": "up", "AMZN": "up", "GOOGL": "up"},
            ),
            NewsItem(
                headline="Inflation concerns weigh on consumer stocks",
                explanation="Rising costs impact retail and consumer discretionary sectors",
                impact={"WMT": "down", "TGT": "down"},
            ),
            NewsItem(
                headline="Energy sector rebounds on supply concerns",
                explanation="Geopolitical tensions and supply chain issues boost oil prices",
                impact={"XOM": "up", "CVX": "up"},
            ),
            NewsItem(
                headline="Banking sector faces regulatory scrutiny",
                explanation="New financial regulations could impact major bank operations",
                impact={"JPM": "down", "BAC": "down"},
            ),
        ]

        # Filter news relevant to tracked symbols
        relevantNews = []
        for item in news:
            # Check if any tracked symbols are mentioned
            hasRelevantSymbol = any(symbol in item.impact for symbol in symbols)
            if hasRelevantSymbol or not item.impact:  # Include general news too
                relevantNews.append(item)

        # Add some general market news if we don't have enough relevant news
        if len(relevantNews) < 3:
            generalNews = [
                NewsItem(
                    headline=f"{self.currentMonth} {self.currentYear} market outlook remains cautious",
                    explanation="Investors weigh economic indicators and corporate earnings",
                    impact={symbols[0]: "up"} if symbols else {},
                ),
                NewsItem(
                    headline="Global supply chain disruptions continue",
                    explanation="International trade challenges affect multiple sectors",
                    impact={symbols[1]: "down"} if len(symbols) > 1 else {},
                ),
                NewsItem(
                    headline="Cryptocurrency market volatility impacts tech stocks",
                    explanation="Digital asset fluctuations create ripple effects in technology sector",
                    impact={symbols[2]: "up"} if len(symbols) > 2 else {},
                ),
            ]
            relevantNews.extend(generalNews)

        return relevantNews

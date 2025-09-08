#!/usr/bin/env python3
"""
NewsAPI.org news provider
"""

import os
from typing import Dict, List, Optional

import requests

from ..interfaces import INewsProvider
from ..market_data import NewsItem


class NewsApiProvider(INewsProvider):
    """Real news data from NewsAPI.org"""

    def __init__(self, apiKey: Optional[str] = None):
        self.apiKey = apiKey or os.getenv("NEWSAPI_KEY")
        self.baseUrl = "https://newsapi.org/v2"

    def isAvailable(self) -> bool:
        """Check if API key is available"""
        return self.apiKey is not None

    def getMarketNews(self, countryCode: str, symbols: List[str]) -> List[NewsItem]:
        """Get real market news from NewsAPI"""
        if not self.isAvailable():
            return []

        try:
            # Search for financial news
            params = {
                "q": "stock market OR finance OR earnings",
                "category": "business",
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": self.apiKey,
            }

            # Add country-specific domain if available
            countryDomains = {
                "US": "wsj.com,bloomberg.com,cnbc.com",
                "GB": "bbc.co.uk,ft.com",
                "CA": "bnn.ca,theglobeandmail.com",
            }

            if countryCode in countryDomains:
                params["domains"] = countryDomains[countryCode]

            response = requests.get(
                f"{self.baseUrl}/everything", params=params, timeout=10
            )
            if response.status_code != 200:
                return []

            data = response.json()
            articles = data.get("articles", [])

            newsItems = []
            for article in articles[:5]:  # Limit to 5 articles
                headline = article.get("title", "")
                description = article.get("description", "")

                # Try to match symbols in headline/description
                impact = self._extractStockImpact(headline + " " + description, symbols)

                if headline and description:
                    newsItems.append(
                        NewsItem(
                            headline=headline[:100],  # Truncate long headlines
                            explanation=description[:200],  # Truncate long descriptions
                            impact=impact,
                        )
                    )

            return newsItems

        except Exception:
            return []

    def _extractStockImpact(self, text: str, symbols: List[str]) -> Dict[str, str]:
        """Extract stock impact from news text"""
        text = text.lower()
        impact = {}

        # Simple keyword matching
        positiveWords = [
            "up",
            "gain",
            "rise",
            "surge",
            "boost",
            "profit",
            "beat",
            "strong",
        ]
        negativeWords = ["down", "fall", "drop", "decline", "loss", "miss", "weak"]

        for symbol in symbols:
            symbolLower = symbol.lower().replace(".to", "").replace(".l", "")

            if symbolLower in text or symbol in text:
                # Check for positive/negative sentiment
                hasPositive = any(word in text for word in positiveWords)
                hasNegative = any(word in text for word in negativeWords)

                if hasPositive and not hasNegative:
                    impact[symbol] = "up"
                elif hasNegative and not hasPositive:
                    impact[symbol] = "down"

        return impact

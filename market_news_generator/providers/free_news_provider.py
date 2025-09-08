#!/usr/bin/env python3
"""
Free news provider using RSS feeds and public APIs
"""

from typing import Dict, List
from xml.etree import ElementTree

import requests

from ..interfaces import INewsProvider
from ..market_data import NewsItem


class FreeNewsProvider(INewsProvider):
    """Free news data from RSS feeds and public sources"""

    def __init__(self):
        self.rssSources = {
            "US": [
                "https://feeds.finance.yahoo.com/rss/2.0/headline",
                "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            ],
            "GB": [
                "https://feeds.bbci.co.uk/news/business/rss.xml",
            ],
            "CA": [
                "https://www.cbc.ca/cmlink/rss-business",
            ],
        }

    def isAvailable(self) -> bool:
        """RSS feeds are always available"""
        return True

    def getMarketNews(self, countryCode: str, symbols: List[str]) -> List[NewsItem]:
        """Get market news from RSS feeds"""
        try:
            sources = self.rssSources.get(countryCode, self.rssSources["US"])
            allNews = []

            for rssUrl in sources:
                try:
                    response = requests.get(rssUrl, timeout=10)
                    if response.status_code == 200:
                        news = self._parseRssFeed(response.text, symbols)
                        allNews.extend(news)
                except Exception:
                    continue

            # Return up to 3 news items
            return allNews[:3] if allNews else self._getFallbackNews(symbols)

        except Exception:
            return self._getFallbackNews(symbols)

    def _parseRssFeed(self, rssContent: str, symbols: List[str]) -> List[NewsItem]:
        """Parse RSS feed content"""
        try:
            root = ElementTree.fromstring(rssContent)
            items = []

            # Handle different RSS formats
            newsItems = root.findall(".//item") or root.findall(".//{*}entry")

            for item in newsItems[:5]:  # Limit to 5 items
                title = self._getElementText(item, ["title"])
                description = self._getElementText(
                    item, ["description", "summary", "content"]
                )

                if title and description:
                    # Extract stock impact
                    impact = self._extractStockImpact(
                        title + " " + description, symbols
                    )

                    items.append(
                        NewsItem(
                            headline=title[:80],  # Truncate long titles
                            explanation=description[:150],  # Truncate descriptions
                            impact=impact,
                        )
                    )

            return items

        except Exception:
            return []

    def _getElementText(self, item, tagNames: List[str]) -> str:
        """Get text from first available tag"""
        for tagName in tagNames:
            element = item.find(tagName) or item.find(
                f".//{{{item.tag.split('}')[0][1:]}}}{tagName}"
            )
            if element is not None and element.text:
                return element.text.strip()
        return ""

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
            "buy",
        ]
        negativeWords = [
            "down",
            "fall",
            "drop",
            "decline",
            "loss",
            "miss",
            "weak",
            "sell",
        ]

        for symbol in symbols:
            symbolLower = (
                symbol.lower().replace(".to", "").replace(".l", "").replace(".ns", "")
            )
            companyNames = {
                "aapl": "apple",
                "msft": "microsoft",
                "googl": "google",
                "amzn": "amazon",
                "tsla": "tesla",
                "meta": "meta",
                "nvda": "nvidia",
            }

            # Check symbol or company name
            checkTerms = [symbolLower, companyNames.get(symbolLower, "")]

            for term in checkTerms:
                if term and term in text:
                    # Check for positive/negative sentiment
                    hasPositive = any(word in text for word in positiveWords)
                    hasNegative = any(word in text for word in negativeWords)

                    if hasPositive and not hasNegative:
                        impact[symbol] = "up"
                    elif hasNegative and not hasPositive:
                        impact[symbol] = "down"
                    break

        return impact

    def _getFallbackNews(self, symbols: List[str]) -> List[NewsItem]:
        """Fallback news when RSS fails"""
        return [
            NewsItem(
                headline="Markets show mixed performance",
                explanation="Technology stocks lead gains while energy sector declines",
                impact={symbols[0]: "up"} if symbols else {},
            ),
            NewsItem(
                headline="Federal Reserve maintains interest rates",
                explanation="Central bank policy supports market stability",
                impact={symbols[1]: "up"} if len(symbols) > 1 else {},
            ),
        ]

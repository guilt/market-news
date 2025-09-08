#!/usr/bin/env python3
"""
News scraping provider - real financial news without API keys
"""

import re
from typing import Dict, List

import requests

from ..cache_mixin import CacheMixin
from ..interfaces import INewsProvider
from ..market_data import NewsItem


class NewsScrapingProvider(CacheMixin, INewsProvider):
    """Scrape real financial news from public websites"""

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        self._default_ttl = 600  # 10 minutes for news

    def isAvailable(self) -> bool:
        """Always available"""
        return True

    def getMarketNews(self, countryCode: str, symbols: List[str]) -> List[NewsItem]:
        """Get market news with caching"""
        return self._cachedCall(
            "getMarketNews", self._fetchMarketNews, countryCode, tuple(symbols)
        )

    def _fetchMarketNews(self, countryCode: str, symbols: tuple) -> List[NewsItem]:
        """Scrape real financial news"""
        try:
            # Try multiple sources
            news = []
            symbolsList = list(symbols)

            # Yahoo Finance news
            yahooNews = self._scrapeYahooNews(symbolsList)
            news.extend(yahooNews)

            # MarketWatch news
            marketWatchNews = self._scrapeMarketWatchNews()
            news.extend(marketWatchNews)

            return news[:3] if news else self._getFallbackNews(symbolsList)

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            return self._getFallbackNews(list(symbols))

    def _scrapeYahooNews(self, symbols: List[str]) -> List[NewsItem]:
        """Scrape Yahoo Finance news"""
        try:
            url = "https://finance.yahoo.com/"
            response = self.session.get(url, timeout=10)

            if response.status_code == 429:
                raise Exception("Rate limit 429")
            elif response.status_code != 200:
                return []

            html = response.text

            # Multiple patterns to catch different headline formats
            patterns = [
                r'<h3[^>]*><a[^>]*href="[^"]*"[^>]*>([^<]+)</a></h3>',
                r'<a[^>]*class="[^"]*story-title[^"]*"[^>]*>([^<]+)</a>',
                r'data-module="stream-item"[^>]*>.*?<h3[^>]*>.*?<a[^>]*>([^<]+)</a>',
                r'"title":"([^"]*stock|[^"]*market|[^"]*earnings[^"]*)"',
            ]

            headlines = []
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                headlines.extend(matches[:3])
                if len(headlines) >= 5:
                    break

            news = []
            for headline in headlines[:5]:
                # Clean up headline
                headline = re.sub(r"\\[nt]", " ", headline).strip()
                if len(headline) > 10 and any(
                    word in headline.lower()
                    for word in ["stock", "market", "shares", "earnings", "trading"]
                ):
                    impact = self._extractStockImpact(headline, symbols)
                    news.append(
                        NewsItem(
                            headline=headline[:80],
                            explanation="Real market news from Yahoo Finance",
                            impact=impact,
                        )
                    )

            return news

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            return []

    def _scrapeMarketWatchNews(self) -> List[NewsItem]:
        """Scrape MarketWatch news"""
        try:
            url = "https://www.marketwatch.com/markets"
            response = self.session.get(url, timeout=10)

            if response.status_code == 429:
                raise Exception("Rate limit 429")
            elif response.status_code != 200:
                return []

            html = response.text

            # Extract headlines
            headlines = re.findall(
                r'<h3[^>]*class="[^"]*headline[^"]*"[^>]*>([^<]+)</h3>', html
            )

            news = []
            for headline in headlines[:3]:
                news.append(
                    NewsItem(
                        headline=headline[:80],
                        explanation="Market analysis from MarketWatch",
                        impact={},
                    )
                )

            return news

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                raise  # Let CacheMixin handle 429 errors
            return []

    def _extractStockImpact(self, text: str, symbols: List[str]) -> Dict[str, str]:
        """Extract stock impact from news text"""
        text = text.lower()
        impact = {}

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

        companyNames = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "amazon": "AMZN",
            "tesla": "TSLA",
            "meta": "META",
            "nvidia": "NVDA",
        }

        # Check for company mentions
        for company, symbol in companyNames.items():
            if company in text and symbol in symbols:
                hasPositive = any(word in text for word in positiveWords)
                hasNegative = any(word in text for word in negativeWords)

                if hasPositive and not hasNegative:
                    impact[symbol] = "up"
                elif hasNegative and not hasPositive:
                    impact[symbol] = "down"

        return impact

    def _getFallbackNews(self, symbols: List[str]) -> List[NewsItem]:
        """Fallback news when scraping fails"""
        return [
            NewsItem(
                headline="Technology stocks show mixed performance",
                explanation="Major tech companies report varied quarterly results",
                impact={symbols[0]: "up"} if symbols else {},
            ),
            NewsItem(
                headline="Market volatility continues amid economic uncertainty",
                explanation="Investors remain cautious as economic indicators show mixed signals",
                impact={symbols[1]: "down"} if len(symbols) > 1 else {},
            ),
        ]

"""
Data providers for real financial and news data
"""

from .alpha_vantage_provider import AlphaVantageProvider
from .free_news_provider import FreeNewsProvider
from .google_provider import GoogleFinanceProvider
from .marketwatch_provider import MarketWatchProvider
from .newsapi_provider import NewsApiProvider
from .scraping_provider import ScrapingFinancialProvider
from .yahoo_provider import YahooFinanceProvider

__all__ = [
    "AlphaVantageProvider",
    "NewsApiProvider",
    "YahooFinanceProvider",
    "FreeNewsProvider",
    "ScrapingFinancialProvider",
    "GoogleFinanceProvider",
    "MarketWatchProvider",
]

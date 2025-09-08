"""
Market News Generator - Live market watch with country detection
"""

__version__ = "0.1.0"
__author__ = "Market News Generator Team"

from .market_data import MarketDataProvider, NewsItem, StockData
from .market_detector import MarketDetector

__all__ = [
    "MarketDataProvider",
    "StockData",
    "NewsItem",
    "MarketDetector",
]

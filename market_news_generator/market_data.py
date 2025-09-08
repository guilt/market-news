#!/usr/bin/env python3
"""
Core market data library with country detection - camelCase style
"""

import os
import random
from typing import Dict, List, NamedTuple, Optional

from .market_detector import MarketDetector


class StockData(NamedTuple):
    symbol: str
    price: float
    change: float
    changePercent: float
    explanation: str


class NewsItem(NamedTuple):
    headline: str
    explanation: str
    impact: Dict[str, str]  # symbol -> "up"/"down"


class MarketDataProvider:
    """Core market data provider with country detection"""

    def __init__(
        self, cacheDir: str = "~/.market_cache", countryCode: Optional[str] = None
    ):
        self.cacheDir = os.path.expanduser(cacheDir)
        os.makedirs(self.cacheDir, exist_ok=True)

        # Auto-detect market
        self.detector = MarketDetector()
        self.marketInfo = self.detector.getMarketInfo(countryCode)
        self.countryCode = self.marketInfo["country"]
        self.topStocks = self.marketInfo["topStocks"]
        self.currency = self.marketInfo["currency"]

        # Base prices for different markets
        self.basePrices = self._getBasePrices()
        self.companyInfo = self._getCompanyInfo()

    def _getBasePrices(self) -> Dict[str, float]:
        """Get base prices based on country/market"""
        if self.countryCode == "US":
            return {
                "AAPL": 225.40,
                "MSFT": 415.60,
                "GOOGL": 175.30,
                "AMZN": 185.20,
                "NVDA": 875.50,
                "TSLA": 248.90,
                "META": 520.80,
                "AVGO": 1650.30,
                "AMD": 142.80,
                "CRM": 285.40,
            }
        elif self.countryCode == "CA":
            return {
                "SHOP.TO": 85.20,
                "CNR.TO": 165.40,
                "RY.TO": 145.80,
                "TD.TO": 78.90,
                "BNS.TO": 72.30,
                "BMO.TO": 135.60,
                "ENB.TO": 58.40,
                "TRI.TO": 195.20,
                "WCN.TO": 185.70,
                "CP.TO": 108.50,
            }
        elif self.countryCode == "GB":
            return {
                "SHEL.L": 28.50,
                "AZN.L": 125.40,
                "LSEG.L": 95.80,
                "UU.L": 10.25,
                "ULVR.L": 45.60,
                "RDSA.L": 28.90,
                "VOD.L": 0.75,
                "BP.L": 4.85,
                "HSBA.L": 6.95,
                "GSK.L": 15.80,
            }
        else:
            # Default to US prices for other markets
            return {
                "AAPL": 225.40,
                "MSFT": 415.60,
                "GOOGL": 175.30,
                "AMZN": 185.20,
                "NVDA": 875.50,
                "TSLA": 248.90,
                "META": 520.80,
                "AVGO": 1650.30,
                "AMD": 142.80,
                "CRM": 285.40,
            }

    def _getCompanyInfo(self) -> Dict[str, str]:
        """Get company descriptions based on market"""
        if self.countryCode == "US":
            return {
                "AAPL": "Apple - iPhones, iPads, Mac computers",
                "MSFT": "Microsoft - Windows, Office, Xbox, cloud",
                "GOOGL": "Google - Search, YouTube, Android",
                "AMZN": "Amazon - Online shopping + AWS cloud",
                "NVDA": "NVIDIA - AI chips that power ChatGPT",
                "TSLA": "Tesla - Electric cars and solar panels",
                "META": "Meta - Facebook, Instagram, WhatsApp, VR",
                "AVGO": "Broadcom - Chips for phones, WiFi, AI servers",
                "AMD": "AMD - Computer chips, competes with Intel/NVIDIA",
                "CRM": "Salesforce - Business customer software",
            }
        elif self.countryCode == "CA":
            return {
                "SHOP.TO": "Shopify - E-commerce platform for businesses",
                "CNR.TO": "Canadian National Railway - Freight transportation",
                "RY.TO": "Royal Bank of Canada - Major Canadian bank",
                "TD.TO": "TD Bank - Banking and financial services",
                "BNS.TO": "Bank of Nova Scotia - International banking",
                "BMO.TO": "Bank of Montreal - Banking services",
                "ENB.TO": "Enbridge - Oil and gas pipeline company",
                "TRI.TO": "Thomson Reuters - News and information services",
                "WCN.TO": "Waste Connections - Waste management services",
                "CP.TO": "Canadian Pacific Railway - Transportation",
            }
        elif self.countryCode == "GB":
            return {
                "SHEL.L": "Shell - Oil and gas energy company",
                "AZN.L": "AstraZeneca - Pharmaceutical company",
                "LSEG.L": "London Stock Exchange Group - Financial markets",
                "UU.L": "United Utilities - Water and wastewater services",
                "ULVR.L": "Unilever - Consumer goods (soap, food)",
                "RDSA.L": "Royal Dutch Shell - Energy company",
                "VOD.L": "Vodafone - Mobile telecommunications",
                "BP.L": "BP - British oil and gas company",
                "HSBA.L": "HSBC - International banking",
                "GSK.L": "GlaxoSmithKline - Pharmaceutical company",
            }
        else:
            return {symbol: f"{symbol} - Major company" for symbol in self.topStocks}

    def getStockData(self, symbol: str) -> StockData:
        """Get current stock data"""
        if symbol not in self.basePrices:
            # Use average price for unknown symbols
            basePrice = 100.0
        else:
            basePrice = self.basePrices[symbol]

        # Simulate price movement
        changePercent = random.uniform(-4.0, 4.0)  # -4% to +4%
        change = basePrice * (changePercent / 100)
        currentPrice = basePrice + change

        # Generate explanation
        explanation = self._generateExplanation(symbol, changePercent)

        return StockData(
            symbol=symbol,
            price=currentPrice,
            change=change,
            changePercent=changePercent,
            explanation=explanation,
        )

    def getAllStocks(self) -> List[StockData]:
        """Get data for all tracked stocks"""
        return [self.getStockData(symbol) for symbol in self.topStocks]

    def getMarketNews(self) -> List[NewsItem]:
        """Get current market news based on country"""
        newsTemplates = self._getNewsTemplates()
        return random.sample(newsTemplates, random.randint(2, 3))

    def _getNewsTemplates(self) -> List[NewsItem]:
        """Get news templates based on market"""
        if self.countryCode == "US":
            return [
                NewsItem(
                    headline="OpenAI partners with Broadcom for custom AI chips",
                    explanation="Broadcom will make specialized chips for OpenAI, reducing NVIDIA dependence",
                    impact={"AVGO": "up", "NVDA": "down"},
                ),
                NewsItem(
                    headline="Apple announces record iPhone sales",
                    explanation="Strong consumer demand despite economic concerns",
                    impact={"AAPL": "up"},
                ),
                NewsItem(
                    headline="Tesla Autopilot gets safety approval",
                    explanation="Self-driving cars closer to reality, Tesla leading",
                    impact={"TSLA": "up"},
                ),
                NewsItem(
                    headline="Meta VR headset sales exceed expectations",
                    explanation="Virtual reality gaining mainstream adoption",
                    impact={"META": "up"},
                ),
            ]
        elif self.countryCode == "CA":
            return [
                NewsItem(
                    headline="Shopify expands into European markets",
                    explanation="E-commerce platform gaining international traction",
                    impact={"SHOP.TO": "up"},
                ),
                NewsItem(
                    headline="Canadian banks report strong quarterly results",
                    explanation="Interest rate environment boosting bank profits",
                    impact={"RY.TO": "up", "TD.TO": "up", "BNS.TO": "up"},
                ),
                NewsItem(
                    headline="Oil pipeline expansion approved",
                    explanation="Enbridge gets regulatory approval for new pipeline",
                    impact={"ENB.TO": "up"},
                ),
            ]
        elif self.countryCode == "GB":
            return [
                NewsItem(
                    headline="Shell reports record quarterly profits",
                    explanation="Oil prices boost energy company revenues",
                    impact={"SHEL.L": "up", "BP.L": "up"},
                ),
                NewsItem(
                    headline="AstraZeneca drug trial shows promising results",
                    explanation="New cancer treatment could boost pharmaceutical revenues",
                    impact={"AZN.L": "up", "GSK.L": "up"},
                ),
                NewsItem(
                    headline="London Stock Exchange sees increased trading volume",
                    explanation="Market volatility driving higher transaction fees",
                    impact={"LSEG.L": "up"},
                ),
                NewsItem(
                    headline="UK utilities face regulatory pressure",
                    explanation="Government considering price caps on water companies",
                    impact={"UU.L": "down"},
                ),
            ]
        else:
            # Generic news for other markets (DE, JP, IN)
            return [
                NewsItem(
                    headline="Global markets show positive momentum",
                    explanation="International trade improving across regions",
                    impact={self.topStocks[0]: "up"},
                ),
                NewsItem(
                    headline="Technology sector leads market gains",
                    explanation="Digital transformation driving growth",
                    impact={self.topStocks[1]: "up"},
                ),
                NewsItem(
                    headline="Central bank policy supports market stability",
                    explanation="Monetary policy providing economic support",
                    impact={self.topStocks[2]: "up"},
                ),
            ]

    def _generateExplanation(self, symbol: str, changePercent: float) -> str:
        """Generate human explanation for price movement"""
        companyDesc = self.companyInfo.get(symbol, f"{symbol} stock")

        if abs(changePercent) < 1.0:
            return f"{companyDesc} - Normal trading"

        if changePercent > 0:
            return f"📈 Strong performance - {companyDesc}"
        else:
            return f"📉 Temporary dip - {companyDesc}"

    def getMarketSummary(self) -> Dict:
        """Get market summary info with user-friendly messaging"""
        countryName = self.detector.getCountryName(self.countryCode)

        # Check if this is a fallback market
        isFallback = self.marketInfo.get("fallback", False)

        summary = {
            "country": countryName,
            "countryCode": self.countryCode,
            "currency": self.currency,
            "indexes": self.marketInfo["indexes"],
            "stockCount": len(self.topStocks),
            "fallback": isFallback,
        }

        if isFallback:
            summary["fallbackMessage"] = f"Showing global markets for {countryName}"

        return summary

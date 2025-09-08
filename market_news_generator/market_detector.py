#!/usr/bin/env python3
"""
Market detector - auto-detect country and top stocks
"""

from typing import Dict, List, Optional

import requests


class MarketDetector:
    """Auto-detect country and find top stocks"""

    def __init__(self):
        self.countryData = {
            "US": {
                "indexes": ["S&P 500", "NASDAQ", "DOW"],
                "topStocks": [
                    "AAPL",
                    "MSFT",
                    "GOOGL",
                    "AMZN",
                    "NVDA",
                    "TSLA",
                    "META",
                    "AVGO",
                    "AMD",
                    "CRM",
                ],
                "currency": "USD",
            },
            "CA": {
                "indexes": ["TSX", "TSX Venture"],
                "topStocks": [
                    "SHOP.TO",
                    "CNR.TO",
                    "RY.TO",
                    "TD.TO",
                    "BNS.TO",
                    "BMO.TO",
                    "ENB.TO",
                    "TRI.TO",
                    "WCN.TO",
                    "CP.TO",
                ],
                "currency": "CAD",
            },
            "GB": {
                "indexes": ["FTSE 100", "FTSE 250"],
                "topStocks": [
                    "SHEL.L",
                    "AZN.L",
                    "LSEG.L",
                    "UU.L",
                    "ULVR.L",
                    "RDSA.L",
                    "VOD.L",
                    "BP.L",
                    "HSBA.L",
                    "GSK.L",
                ],
                "currency": "GBP",
            },
            "DE": {
                "indexes": ["DAX", "MDAX"],
                "topStocks": [
                    "SAP.DE",
                    "ASML.AS",
                    "NVDA",
                    "TSLA",
                    "META",
                    "GOOGL",
                    "AAPL",
                    "MSFT",
                    "AMZN",
                    "AMD",
                ],
                "currency": "EUR",
            },
            "JP": {
                "indexes": ["Nikkei 225", "TOPIX"],
                "topStocks": [
                    "7203.T",
                    "6758.T",
                    "9984.T",
                    "6861.T",
                    "8306.T",
                    "9432.T",
                    "4063.T",
                    "6098.T",
                    "7974.T",
                    "8035.T",
                ],
                "currency": "JPY",
            },
            "IN": {
                "indexes": ["SENSEX", "NIFTY 50"],
                "topStocks": [
                    "RELIANCE.NS",
                    "TCS.NS",
                    "HDFCBANK.NS",
                    "INFY.NS",
                    "HINDUNILVR.NS",
                    "ICICIBANK.NS",
                    "SBIN.NS",
                    "BHARTIARTL.NS",
                    "ITC.NS",
                    "KOTAKBANK.NS",
                ],
                "currency": "INR",
            },
        }

    def detectCountry(self) -> str:
        """Auto-detect country from IP geolocation"""
        try:
            # Use free IP geolocation service
            response = requests.get("http://ip-api.com/json/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                countryCode = data.get("countryCode", "US")
                return countryCode if countryCode in self.countryData else "US"
        except Exception:
            pass
        return "US"  # Default fallback

    def getMarketInfo(self, countryCode: Optional[str] = None) -> Dict:
        """Get market info for country with graceful fallback"""
        if not countryCode:
            countryCode = self.detectCountry()

        # Graceful fallback for unsupported countries
        if countryCode not in self.countryData:
            # Use US market as fallback but show original country name
            marketInfo = self.countryData["US"].copy()
            return {
                "country": countryCode,  # Keep original country code
                "indexes": ["Global Markets"],  # Generic index name
                "topStocks": marketInfo["topStocks"],  # Use US stocks as global
                "currency": "USD",  # Default to USD
                "fallback": True,  # Flag to indicate this is a fallback
            }

        marketInfo = self.countryData[countryCode]
        return {
            "country": countryCode,
            "indexes": marketInfo["indexes"],
            "topStocks": marketInfo["topStocks"],
            "currency": marketInfo["currency"],
            "fallback": False,
        }

    def getTopStocks(self, countryCode: Optional[str] = None) -> List[str]:
        """Get top stocks for country"""
        marketInfo = self.getMarketInfo(countryCode)
        return marketInfo["topStocks"]

    def getCountryName(self, countryCode: str) -> str:
        """Get full country name with fallback"""
        countryNames = {
            "US": "United States",
            "CA": "Canada",
            "GB": "United Kingdom",
            "DE": "Germany",
            "JP": "Japan",
            "IN": "India",
            # Add more common countries
            "FR": "France",
            "IT": "Italy",
            "ES": "Spain",
            "NL": "Netherlands",
            "AU": "Australia",
            "BR": "Brazil",
            "MX": "Mexico",
            "KR": "South Korea",
            "CN": "China",
            "RU": "Russia",
            "SG": "Singapore",
            "HK": "Hong Kong",
            "CH": "Switzerland",
            "SE": "Sweden",
            "NO": "Norway",
            "DK": "Denmark",
        }
        return countryNames.get(countryCode, f"{countryCode} (Global Market)")

"""
Market Data Triangulation Layer
Cross-references yfinance vs Alpha Vantage for price verification.
Discrepancies between sources trigger risk penalties.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import requests

from app.core.config import settings
from app.core.cache import SimpleCache


# Price data cache (5 minute TTL)
price_cache = SimpleCache(ttl_seconds=300)


class MarketDataTriangulator:
    """
    Fetches the SAME data point from multiple sources and compares.
    Discrepancies trigger red flags and risk penalties.
    """
    
    def __init__(self):
        self.alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY")
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def verify_price_data(self, ticker: str) -> Dict[str, Any]:
        """
        Cross-check current price from yfinance vs Alpha Vantage.
        
        Returns:
            {
                "yfinance_price": float,
                "alphavantage_price": float,
                "deviation_percent": float,
                "data_quality": str,  # "EXCELLENT", "ACCEPTABLE", "DISCREPANCY", "NO_DATA"
                "source_agreement": bool,
                "risk_penalty": int
            }
        """
        # Check cache first
        cache_key = f"triangulated_price:{ticker}"
        cached = price_cache.get(cache_key)
        if cached:
            return cached
        
        # Fetch from both sources concurrently
        loop = asyncio.get_event_loop()
        
        yf_task = loop.run_in_executor(
            self.executor, 
            self._fetch_yfinance_price, 
            ticker
        )
        av_task = loop.run_in_executor(
            self.executor, 
            self._fetch_alphavantage_price, 
            ticker
        )
        
        yf_data, av_data = await asyncio.gather(yf_task, av_task)
        
        result = self._compare_prices(ticker, yf_data, av_data)
        
        # Cache successful results
        if result["data_quality"] != "NO_DATA":
            price_cache.set(cache_key, result)
        
        return result
    
    def _fetch_yfinance_price(self, ticker: str) -> Optional[float]:
        """Fetch current price from yfinance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try multiple price fields
            price = (
                info.get("currentPrice") or 
                info.get("regularMarketPrice") or 
                info.get("previousClose")
            )
            
            if price and price > 0:
                return float(price)
            return None
            
        except Exception as e:
            print(f"⚠️ yfinance error for {ticker}: {e}")
            return None
    
    def _fetch_alphavantage_price(self, ticker: str) -> Optional[float]:
        """Fetch current price from Alpha Vantage."""
        if not self.alphavantage_key:
            return None
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": self.alphavantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            quote = data.get("Global Quote", {})
            price_str = quote.get("05. price")
            
            if price_str:
                return float(price_str)
            return None
            
        except Exception as e:
            print(f"⚠️ Alpha Vantage error for {ticker}: {e}")
            return None
    
    def _compare_prices(
        self, 
        ticker: str, 
        yf_price: Optional[float], 
        av_price: Optional[float]
    ) -> Dict[str, Any]:
        """Compare prices from both sources and determine data quality."""
        
        # Case 1: No data from any source
        if yf_price is None and av_price is None:
            return {
                "ticker": ticker,
                "yfinance_price": None,
                "alphavantage_price": None,
                "deviation_percent": None,
                "data_quality": "NO_DATA",
                "source_agreement": False,
                "risk_penalty": 100,  # Auto-refuse
                "reason": "No market data available from ANY source"
            }
        
        # Case 2: Only one source has data
        if yf_price is None or av_price is None:
            available_price = yf_price or av_price
            source = "yfinance" if yf_price else "alphavantage"
            return {
                "ticker": ticker,
                "yfinance_price": yf_price,
                "alphavantage_price": av_price,
                "available_price": available_price,
                "deviation_percent": None,
                "data_quality": "SINGLE_SOURCE",
                "source_agreement": False,
                "risk_penalty": 40,
                "reason": f"Only {source} available"
            }
        
        # Case 3: Both sources available - compare deviation
        deviation = abs(yf_price - av_price) / yf_price * 100
        
        if deviation < 1.0:
            # Prices match within 1% - EXCELLENT
            quality = "EXCELLENT"
            agreement = True
            risk_penalty = 0
        elif deviation < 5.0:
            # Prices within 5% - ACCEPTABLE
            quality = "ACCEPTABLE"
            agreement = True
            risk_penalty = 10
        else:
            # Prices differ significantly - DISCREPANCY
            quality = "DISCREPANCY"
            agreement = False
            risk_penalty = 50
        
        return {
            "ticker": ticker,
            "yfinance_price": round(yf_price, 2),
            "alphavantage_price": round(av_price, 2),
            "deviation_percent": round(deviation, 2),
            "data_quality": quality,
            "source_agreement": agreement,
            "risk_penalty": risk_penalty,
            "average_price": round((yf_price + av_price) / 2, 2)
        }
    
    async def verify_fundamental_claim(
        self,
        ticker: str,
        claim: str
    ) -> Dict[str, Any]:
        """
        Verify fundamental claims about revenue, earnings, etc.
        Uses yfinance fundamentals data.
        """
        try:
            loop = asyncio.get_event_loop()
            fundamentals = await loop.run_in_executor(
                self.executor,
                self._fetch_fundamentals,
                ticker
            )
            
            if not fundamentals:
                return {
                    "ticker": ticker,
                    "fundamentals_available": False,
                    "claim_supported": None,
                    "reason": "Unable to fetch fundamental data"
                }
            
            # Analyze claim against fundamentals
            claim_analysis = self._analyze_claim_vs_fundamentals(claim, fundamentals)
            
            return {
                "ticker": ticker,
                "fundamentals_available": True,
                "fundamentals": fundamentals,
                "claim_analysis": claim_analysis,
                "claim_supported": claim_analysis.get("supported")
            }
            
        except Exception as e:
            return {
                "ticker": ticker,
                "fundamentals_available": False,
                "error": str(e)
            }
    
    def _fetch_fundamentals(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch key fundamental data from yfinance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "market_cap": info.get("marketCap"),
                "revenue": info.get("totalRevenue"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings": info.get("netIncomeToCommon"),
                "profit_margin": info.get("profitMargins"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow")
            }
        except Exception as e:
            print(f"⚠️ Fundamentals error for {ticker}: {e}")
            return None
    
    def _analyze_claim_vs_fundamentals(
        self, 
        claim: str, 
        fundamentals: Dict
    ) -> Dict[str, Any]:
        """Simple heuristic analysis of claim vs fundamental data."""
        claim_lower = claim.lower()
        analysis = {"supported": None, "evidence": []}
        
        # Check revenue growth claims
        if any(word in claim_lower for word in ["revenue", "sales", "growing"]):
            growth = fundamentals.get("revenue_growth")
            if growth is not None:
                if growth > 0.1:  # > 10% growth
                    analysis["evidence"].append(f"Revenue growth: {growth*100:.1f}%")
                    analysis["supported"] = True
                elif growth < 0:
                    analysis["evidence"].append(f"Revenue declining: {growth*100:.1f}%")
                    analysis["supported"] = False
        
        # Check profitability claims
        if any(word in claim_lower for word in ["profit", "earnings", "profitable"]):
            margin = fundamentals.get("profit_margin")
            if margin is not None:
                if margin > 0.1:
                    analysis["evidence"].append(f"Profit margin: {margin*100:.1f}%")
                    analysis["supported"] = True
                elif margin < 0:
                    analysis["evidence"].append("Company is not profitable")
                    analysis["supported"] = False
        
        return analysis


# Singleton instance
market_triangulator = MarketDataTriangulator()

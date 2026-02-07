import os
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from typing import Dict, Any, Optional

class MarketDataManager:
    def __init__(self):
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        
        self.ts = None
        if self.api_key:
            try:
                self.ts = TimeSeries(key=self.api_key, output_format='json')
                print("✅ Alpha Vantage Initialized")
            except Exception as e:
                print(f"⚠️ Alpha Vantage Init Failed: {e}. Falling back to YFinance.")
                self.ts = None
        else:
            print("ℹ️ Alpha Vantage Key Missing (Using YFinance Fallback)")

    def get_realtime_price(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Get real-time price using Alpha Vantage > YFinance
        """
        # Alpha Vantage uses symbol.BSE or symbol.NSE
        av_symbol = f"{symbol}.{exchange}" if exchange in ["BSE", "NSE"] else symbol
        
        if self.ts:
            try:
                # Get Quote Endpoint (Global Quote)
                data, _ = self.ts.get_quote_endpoint(symbol=av_symbol)
                quote = data
                return {
                    "Current Price": float(quote['05. price']),
                    "Change": float(quote['09. change']),
                    "Change %": float(quote['10. change percent'].strip('%')),
                    "Volume": int(quote['06. volume']),
                    "Timestamp": quote['07. latest trading day'],
                    "Source": "Alpha Vantage (Realtime)"
                }
            except Exception as e:
                print(f"⚠️ Alpha Vantage Fetch Error ({av_symbol}): {e}")
        
        # Fallback to YFinance
        return self._get_yfinance_price(symbol, exchange)

    def _get_yfinance_price(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """YFinance Fallback Implementation"""
        suffix = ".NS" if exchange == "NSE" else ".BO"
        ticker = yf.Ticker(f"{symbol}{suffix}")
        info = ticker.info
        return {
            "Current Price": info.get("currentPrice", info.get("regularMarketPrice")),
            "Change (Day)": info.get("regularMarketChange"),
            "Change %": info.get("regularMarketChangePercent"),
            "Target Price": info.get("targetMeanPrice"),
            "Source": "Yahoo Finance (Delayed)"
        }

    # ... get_fundamentals remains same ...
    def get_fundamentals(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Get fundamental data (YFinance/Tickertape is better for this)
        """
        suffix = ".NS" if exchange == "NSE" else ".BO"
        ticker = yf.Ticker(f"{symbol}{suffix}")
        info = ticker.info
        
        return {
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "PB Ratio": info.get("priceToBook"),
            "EPS": info.get("trailingEps"),
            "ROE": info.get("returnOnEquity"),
            "Sector": info.get("sector"),
            "Source": "Yahoo Finance (Fundamentals)"
        }

# Singleton Instance
market_data_manager = MarketDataManager()

import os
import yfinance as yf
from breeze_connect import BreezeConnect
from typing import Dict, Any, Optional

class MarketDataManager:
    def __init__(self):
        self.api_key = os.getenv("BREEZE_API_KEY")
        self.api_secret = os.getenv("BREEZE_API_SECRET")
        self.session_token = os.getenv("BREEZE_SESSION_TOKEN")
        
        self.breeze = None
        if self.api_key and self.api_secret and self.session_token:
            try:
                self.breeze = BreezeConnect(api_key=self.api_key)
                self.breeze.generate_session(api_secret=self.api_secret, session_token=self.session_token)
                print("✅ Breeze Connect Initialized (Primary Data Source)")
            except Exception as e:
                print(f"⚠️ Breeze Connect Init Failed: {e}. Falling back to YFinance.")
                self.breeze = None
        else:
            print("ℹ️ Breeze Credentials Missing (Using YFinance Fallback)")

    def get_realtime_price(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Get real-time price using the best available source (Breeze > YFinance)
        """
        if self.breeze:
            try:
                # Breeze API call (Example logic, adapt to actual API)
                data = self.breeze.get_quotes(stock_code=symbol, exchange_code=exchange, product_type="cash", right="others", get_exchange_quotes=True)
                if data and 'Success' in data and data['Success']:
                   quote = data['Success'][0]
                   return {
                       "Current Price": float(quote['ltp']),
                       "Change": float(quote['change']),
                       "Change %": float(quote['change_per']),
                       "Volume": int(quote['total_quantity']),
                       "Timestamp": quote['ltt'],
                       "Source": "Breeze (Realtime)"
                   }
            except Exception as e:
                print(f"⚠️ Breeze Fetch Error ({symbol}): {e}")
        
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

    def get_fundamentals(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Get fundamental data (Usually better from YFinance/Tickertape than Broker APIs)
        """
        # YFinance is actually better for *comprehensive* fundamentals out of the box
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

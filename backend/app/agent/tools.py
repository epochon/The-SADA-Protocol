from typing import Dict, List, Any
import yfinance as yf
from app.agent.analysis import StockAnalysisAgent

def get_realtime_price(symbol: str) -> Dict[str, Any]:
    """
    Get the current realtime price of a stock or crypto.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        return {
            "symbol": symbol,
            "price": info.last_price,
            "currency": info.currency
        }
    except Exception as e:
        return {"error": str(e)}

def get_company_info(symbol: str) -> Dict[str, Any]:
    """
    Get fundamental information about a company.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "name": info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "summary": info.get("longBusinessSummary"),
            "marketCap": info.get("marketCap"),
            "52WeekHigh": info.get("fiftyTwoWeekHigh"),
            "52WeekLow": info.get("fiftyTwoWeekLow")
        }
    except Exception as e:
        return {"error": str(e)}

def get_indian_stock_analysis(symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
    """
    Detailed analysis for Indian stocks.
    """
    agent = StockAnalysisAgent()
    return agent.analyze_stock(symbol, exchange)

def get_available_tools() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_realtime_price",
                "description": "Get the current stock price for a given symbol (e.g. AAPL, BTC-USD).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g. AAPL)"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_company_info",
                "description": "Get fundamental information about a company (sector, summary, market cap).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g. MSFT)"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_indian_stock_analysis",
                "description": "Get a comprehensive analysis for an Indian stock (NSE/BSE).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g. RELIANCE, TCS)"
                        },
                        "exchange": {
                            "type": "string",
                            "enum": ["NSE", "BSE"],
                            "description": "The exchange to query (default: NSE)"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        }
    ]

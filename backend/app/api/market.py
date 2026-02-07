from fastapi import APIRouter, HTTPException
import yfinance as yf
from typing import List, Dict

router = APIRouter()

STOCK_SYMBOLS = ["SPY", "QQQ", "BTC-USD", "ETH-USD", "AAPL", "NVDA", "TSLA"]

@router.get("/ticker", response_model=List[Dict])
def get_market_ticker():
    """
    Fetch real-time market data for the ticker.
    Returns symbol, price, change, and percent change.
    """
    data = []
    
    # Using Tickers for batch processing (more efficient)
    tickers = yf.Tickers(" ".join(STOCK_SYMBOLS))
    
    for symbol in STOCK_SYMBOLS:
        try:
            ticker = tickers.tickers[symbol]
            # Use fast_info for critical data points (faster than .info)
            price = ticker.fast_info.last_price
            prev_close = ticker.fast_info.previous_close
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            data.append({
                "symbol": symbol.replace("-USD", ""), # Clean up crypto names
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2)
            })
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            # Fallback for error, maybe skip or return dummy
            continue
            
    return data

@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "shortName": info.get("shortName"),
            "price": info.get("currentPrice", info.get("regularMarketPrice")),
            "marketCap": info.get("marketCap"),
            "peRatio": info.get("trailingPE"),
            "dayHigh": info.get("dayHigh"),
            "dayLow": info.get("dayLow"),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found or API error: {str(e)}")

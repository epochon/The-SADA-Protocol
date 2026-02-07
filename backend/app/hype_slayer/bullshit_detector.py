"""
Bullshit Score Calculator
Deterministic (non-LLM) rules for detecting obvious scams
"""

import yfinance as yf
from typing import Dict, Any


# Hard-coded thresholds for BS detection
THRESHOLDS = {
    "no_data_penalty": 100,           # No yfinance data = auto-refuse
    "price_deviation_threshold": 1000,  # 1000% = extreme claim
    "price_deviation_penalty": 50,
    "unknown_ticker_penalty": 80,
    "penny_stock_penalty": 20,        # Stocks under $1
    "crypto_meme_penalty": 30,        # Meme coins can be suspicious
}


def calculate_bullshit_score(ticker: str, claimed_price: float = None) -> Dict[str, Any]:
    """
    Calculate deterministic bullshit score for a ticker.
    This is rule-based, NO LLM involved.
    
    Args:
        ticker: The ticker symbol to check
        claimed_price: Optional price claim to verify
        
    Returns:
        dict: BS score and auto-refuse decision
    """
    score = 0
    reasons = []
    
    # Step 1: Check if ticker exists in yfinance
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Check for valid data
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        
        if current_price is None:
            score += THRESHOLDS["no_data_penalty"]
            reasons.append(f"No market data available for '{ticker}'")
        else:
            # Step 2: Check for penny stocks
            if current_price < 1.0:
                score += THRESHOLDS["penny_stock_penalty"]
                reasons.append(f"Penny stock (price: ${current_price:.4f})")
            
            # Step 3: Check claimed price deviation
            if claimed_price is not None and current_price > 0:
                deviation = abs(claimed_price - current_price) / current_price * 100
                
                if deviation > THRESHOLDS["price_deviation_threshold"]:
                    score += THRESHOLDS["price_deviation_penalty"]
                    reasons.append(f"Claimed price ${claimed_price} deviates {deviation:.0f}% from actual ${current_price:.2f}")
            
            # Step 4: Check for meme-coin patterns
            name = (info.get("shortName") or info.get("longName") or "").lower()
            meme_indicators = ["doge", "shib", "pepe", "meme", "moon", "elon", "safe"]
            if any(ind in name for ind in meme_indicators):
                score += THRESHOLDS["crypto_meme_penalty"]
                reasons.append(f"Meme-coin indicator in name: '{name}'")
            
            # Step 5: Check market cap (very low = risky)
            market_cap = info.get("marketCap")
            if market_cap and market_cap < 10_000_000:  # Under $10M
                score += 25
                reasons.append(f"Micro-cap asset (Market cap: ${market_cap:,})")
                
    except Exception as e:
        score += THRESHOLDS["unknown_ticker_penalty"]
        reasons.append(f"Failed to fetch data for '{ticker}': {str(e)}")
    
    # Determine auto-refuse
    auto_refuse = score >= 80
    
    return {
        "bullshit_score": min(score, 100),
        "auto_refuse": auto_refuse,
        "ticker": ticker,
        "reasons": reasons if reasons else ["Ticker appears legitimate"],
        "thresholds_used": THRESHOLDS
    }


def quick_ticker_check(ticker: str) -> Dict[str, Any]:
    """
    Quick check if a ticker is valid and tradeable.
    Used as fast pre-filter before full analysis.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        
        return {
            "valid": info.last_price is not None,
            "ticker": ticker,
            "price": info.last_price if info.last_price else None,
            "currency": getattr(info, 'currency', None)
        }
    except:
        return {
            "valid": False,
            "ticker": ticker,
            "price": None,
            "error": "Ticker not found"
        }


def is_known_scam_pattern(text: str) -> Dict[str, Any]:
    """
    Check text for known scam patterns.
    Returns immediate red flags for obvious scams.
    """
    text_lower = text.lower()
    
    scam_patterns = [
        ("pump and dump", "Explicit pump and dump mention"),
        ("guaranteed returns", "Impossible guarantee claim"),
        ("risk free", "False risk-free claim"),
        ("double your money", "Classic scam promise"),
        ("send me btc", "Crypto scam indicator"),
        ("giveaway scam", "Giveaway scam pattern"),
        ("limited spots", "Artificial scarcity tactic"),
        ("act now or lose", "High-pressure scam tactic"),
    ]
    
    matches = []
    for pattern, description in scam_patterns:
        if pattern in text_lower:
            matches.append({"pattern": pattern, "description": description})
    
    return {
        "has_scam_pattern": len(matches) > 0,
        "matches": matches,
        "scam_score": min(len(matches) * 30, 100)
    }

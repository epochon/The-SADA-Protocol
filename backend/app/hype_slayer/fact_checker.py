from app.services.market_data import market_data_manager
from typing import Dict, Any, List, Optional
from datetime import datetime
import yfinance as yf


def verify_claim(ticker: str, claim: str, claim_type: str = "general", asset_type: str = "stock") -> Dict[str, Any]:
    """
    Verify a financial claim against real market data.
    Uses MarketDataManager for improved accuracy (Alpha Vantage + YFinance Fallback).
    
    Args:
        ticker: Stock/crypto ticker symbol (e.g., RELIANCE, BTC, AAPL)
        claim: The claim being made
        claim_type: One of "price_prediction", "revenue", "earnings", "growth", "general"
        asset_type: "stock" or "crypto"
        
    Returns:
        dict: Verification result with discrepancy analysis
    """
    try:
        # Normalize ticker for YFinance/Alpha Vantage
        normalized_ticker = ticker
        exchange = "NSE" # Default for HypeSlayer target audience
        
        if asset_type == "crypto":
            if not ticker.endswith("-USD"):
                normalized_ticker = f"{ticker}-USD"
        elif asset_type == "stock":
            # If no suffix and looks like an Indian stock (usually uppercase only, 1-10 chars)
            if "." not in ticker and len(ticker) <= 12:
                # We try NSE first as default
                normalized_ticker = f"{ticker}.NS"
        
        # 1. Try to get data via MarketDataManager (which uses Alpha Vantage > YFinance)
        # Note: market_data_manager expects base symbol and exchange separately for AV
        base_symbol = ticker.split('.')[0] if '.' in ticker else ticker
        market_info = market_data_manager.get_realtime_price(base_symbol, exchange)
        fundamentals = market_data_manager.get_fundamentals(base_symbol, exchange)
        
        # Merge data
        stock = yf.Ticker(normalized_ticker)
        yf_info = stock.info
        
        # Check if we got valid price data
        current_price = market_info.get("Current Price") or yf_info.get('regularMarketPrice') or yf_info.get('currentPrice')
        
        if current_price is None:
            return {
                "verification_status": "no_data",
                "ticker": ticker,
                "real_data": None,
                "discrepancy_score": 100,
                "evidence_quality": 0.0,
                "error": f"No market data available for ticker: {ticker}. Try adding exchange suffix (e.g. .NS for NSE or -USD for Crypto)."
            }
        
        # Gather comprehensive real data
        real_data = gather_real_data(stock, yf_info, market_info, fundamentals)
        
        # Calculate evidence quality based on data completeness
        evidence_quality = calculate_evidence_quality(real_data)
        
        # Analyze claim for discrepancies
        discrepancy_result = analyze_discrepancy(claim, claim_type, real_data)
        
        return {
            "verification_status": discrepancy_result["status"],
            "ticker": normalized_ticker,
            "company_name": yf_info.get("shortName", ticker),
            "real_data": real_data,
            "discrepancy_score": discrepancy_result["score"],
            "discrepancy_details": discrepancy_result["details"],
            "evidence_quality": evidence_quality,
            "data_freshness": datetime.now().isoformat(),
            "source": market_info.get("Source", "Mixed")
        }
        
    except Exception as e:
        return {
            "verification_status": "error",
            "ticker": ticker,
            "real_data": None,
            "discrepancy_score": 100,
            "evidence_quality": 0.0,
            "error": str(e)
        }


def gather_real_data(stock, info: Dict, market_info: Dict, fundamentals: Dict) -> Dict[str, Any]:
    """Gather comprehensive real market data merging multiple sources."""
    data = {
        # Current pricing (Prioritizing realtime source)
        "current_price": market_info.get("Current Price") or info.get("currentPrice") or info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose") or market_info.get("Previous Close"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "52_week_high": info.get("fiftyTwoWeekHigh") or fundamentals.get("52WeekHigh"),
        "52_week_low": info.get("fiftyTwoWeekLow") or fundamentals.get("52WeekLow"),
        
        # Valuation (Prioritizing fundamentals source)
        "market_cap": fundamentals.get("Market Cap") or info.get("marketCap"),
        "pe_ratio": fundamentals.get("PE Ratio") or info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "pb_ratio": fundamentals.get("PB Ratio") or info.get("priceToBook"),
        "eps": fundamentals.get("EPS") or info.get("trailingEps"),
        "roe": fundamentals.get("ROE") or info.get("returnOnEquity"),
        
        # Financials
        "revenue": info.get("totalRevenue"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "profit_margin": info.get("profitMargins"),
        "ebitda": info.get("ebitda"),
        
        # Analyst data
        "target_mean_price": info.get("targetMeanPrice") or market_info.get("Target Price"),
        "target_high_price": info.get("targetHighPrice"),
        "target_low_price": info.get("targetLowPrice"),
        "recommendation": info.get("recommendationKey"),
        "num_analyst_opinions": info.get("numberOfAnalystOpinions"),
        "sector": fundamentals.get("Sector") or info.get("sector"),
    }
    
    # Get historical price data for trend analysis
    try:
        hist = stock.history(period="3mo")
        if not hist.empty:
            data["price_3mo_ago"] = float(hist['Close'].iloc[0])
            data["price_1mo_ago"] = float(hist['Close'].iloc[-22]) if len(hist) > 22 else None
            data["price_change_3mo_pct"] = ((data["current_price"] - data["price_3mo_ago"]) / data["price_3mo_ago"] * 100) if data["price_3mo_ago"] else None
    except:
        pass
    
    return data


def calculate_evidence_quality(data: Dict) -> float:
    """Calculate evidence quality score (0.0 to 1.0) based on data completeness."""
    critical_fields = [
        "current_price", "market_cap", "pe_ratio", "revenue", 
        "target_mean_price", "recommendation"
    ]
    
    available = sum(1 for field in critical_fields if data.get(field) is not None)
    return round(available / len(critical_fields), 2)


def analyze_discrepancy(claim: str, claim_type: str, real_data: Dict) -> Dict[str, Any]:
    """
    Analyze discrepancy between claim and real data.
    Returns score 0-100 where higher = more discrepancy/suspicious.
    """
    details = []
    score = 0
    
    claim_lower = claim.lower()
    
    # Check for extreme price predictions
    if claim_type == "price_prediction":
        current = real_data.get("current_price", 0)
        target_high = real_data.get("target_high_price", 0)
        
        # Look for specific price mentions in claim
        import re
        price_matches = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', claim)
        
        if price_matches and current:
            claimed_price = float(price_matches[0].replace(',', ''))
            deviation = abs(claimed_price - current) / current * 100
            
            if deviation > 100:  # Claim is 100%+ away from current price
                score += 40
                details.append(f"Claimed price ${claimed_price} is {deviation:.0f}% away from current ${current:.2f}")
            
            if target_high and claimed_price > target_high * 2:
                score += 30
                details.append(f"Claimed price exceeds 2x analyst high target (${target_high})")
    
    # Check for revenue/growth claims
    if claim_type in ["revenue", "growth", "earnings"]:
        actual_growth = real_data.get("revenue_growth") or real_data.get("earnings_growth")
        
        if "skyrocketing" in claim_lower or "exploding" in claim_lower or "moon" in claim_lower:
            if actual_growth is not None and actual_growth < 0.2:  # Less than 20% growth
                score += 35
                details.append(f"Hyperbolic growth claim, but actual growth is {actual_growth*100:.1f}%")
    
    # Check recommendation alignment
    recommendation = real_data.get("recommendation", "").lower()
    if recommendation in ["sell", "underperform"] and any(word in claim_lower for word in ["buy", "bullish", "going up"]):
        score += 25
        details.append(f"Bullish claim contradicts analyst '{recommendation}' rating")
    
    # Determine status
    if score >= 50:
        status = "discrepancy"
    elif score >= 25:
        status = "caution"
    else:
        status = "aligned"
    
    return {
        "status": status,
        "score": min(score, 100),
        "details": details if details else ["No significant discrepancies detected"]
    }


def get_quarterly_data(ticker: str) -> Optional[List[Dict]]:
    """Get quarterly financial data for deeper verification."""
    try:
        stock = yf.Ticker(ticker)
        quarterly = stock.quarterly_financials
        
        if quarterly is not None and not quarterly.empty:
            return [
                {
                    "period": str(col),
                    "revenue": float(quarterly.loc['Total Revenue', col]) if 'Total Revenue' in quarterly.index else None,
                    "net_income": float(quarterly.loc['Net Income', col]) if 'Net Income' in quarterly.index else None,
                }
                for col in quarterly.columns[:4]  # Last 4 quarters
            ]
    except:
        pass
    return None

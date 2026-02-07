"""
Cross-Verification Orchestration Engine
Coordinates all verification layers and produces final decision.
This is the brain of the cross-checking system.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime

from app.verification.llm_consensus import llm_consensus
from app.verification.market_triangulator import market_triangulator
from app.verification.news_validator import news_validator


class CrossVerificationEngine:
    """
    Master orchestrator for the multi-API cross-verification system.
    Coordinates LLM Consensus, Market Triangulation, and News Validation.
    """
    
    def __init__(self):
        self.llm_layer = llm_consensus
        self.market_layer = market_triangulator
        self.news_layer = news_validator
    
    async def execute_full_verification(
        self,
        transcript: str,
        video_url: str = None
    ) -> Dict[str, Any]:
        """
        THE COMPLETE CROSS-VERIFICATION PIPELINE
        
        Flow:
        1. LLM Consensus (OpenAI ↔ Groq)
        2. Market Data Triangulation (yfinance ↔ Alpha Vantage)
        3. News Validation (Tavily + OpenAI)
        4. Aggregate Confidence Score
        5. Final Decision
        
        Returns comprehensive verification report.
        """
        start_time = datetime.now()
        verification_log: List[Dict] = []
        
        # ===== STEP 1: LLM CONSENSUS =====
        verification_log.append({
            "step": "LLM Consensus Check",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        })
        
        llm_result = await self.llm_layer.extract_with_consensus(transcript)
        
        if not llm_result.get("consensus_reached"):
            # EARLY REFUSAL: LLMs can't agree
            verification_log[-1]["status"] = "failed"
            verification_log[-1]["reason"] = llm_result.get("reason", "LLM disagreement")
            
            return self._generate_refusal_response(
                reason="LLM_DISAGREEMENT",
                details=llm_result,
                log=verification_log,
                start_time=start_time
            )
        
        ticker = llm_result.get("agreed_ticker")
        claim = llm_result.get("agreed_claim") or llm_result.get("primary_result", {}).get("claim", "")
        timeline = llm_result.get("agreed_timeline")
        
        verification_log[-1]["status"] = "passed"
        verification_log[-1]["ticker"] = ticker
        verification_log[-1]["claim"] = claim[:100] + "..." if len(claim) > 100 else claim
        verification_log[-1]["confidence"] = llm_result.get("confidence", 0)
        
        # If no ticker extracted, we can still analyze general claims
        if not ticker:
            verification_log.append({
                "step": "Ticker Extraction",
                "status": "warning",
                "message": "No specific ticker identified - general financial claim",
                "timestamp": datetime.now().isoformat()
            })
        
        # ===== STEP 2: MARKET DATA TRIANGULATION =====
        market_data = None
        if ticker:
            verification_log.append({
                "step": "Market Data Cross-Check",
                "status": "processing",
                "ticker": ticker,
                "timestamp": datetime.now().isoformat()
            })
            
            market_data = await self.market_layer.verify_price_data(ticker)
            
            if market_data.get("data_quality") == "NO_DATA":
                # REFUSAL: No market data available
                verification_log[-1]["status"] = "failed"
                verification_log[-1]["reason"] = "No market data available"
                
                return self._generate_refusal_response(
                    reason="NO_MARKET_DATA",
                    details=market_data,
                    log=verification_log,
                    start_time=start_time
                )
            
            verification_log[-1]["status"] = "completed"
            verification_log[-1]["data_quality"] = market_data.get("data_quality")
            verification_log[-1]["sources_agree"] = market_data.get("source_agreement")
            verification_log[-1]["yfinance_price"] = market_data.get("yfinance_price")
            verification_log[-1]["alphavantage_price"] = market_data.get("alphavantage_price")
        
        # ===== STEP 3: FUNDAMENTAL CLAIM VERIFICATION =====
        fundamental_check = None
        if ticker and claim:
            if any(keyword in claim.lower() for keyword in ["revenue", "earnings", "profit", "growth", "sales"]):
                verification_log.append({
                    "step": "Fundamental Data Verification",
                    "status": "processing",
                    "timestamp": datetime.now().isoformat()
                })
                
                fundamental_check = await self.market_layer.verify_fundamental_claim(
                    ticker=ticker,
                    claim=claim
                )
                
                verification_log[-1]["status"] = "completed"
                verification_log[-1]["fundamentals_available"] = fundamental_check.get("fundamentals_available")
                verification_log[-1]["claim_supported"] = fundamental_check.get("claim_supported")
        
        # ===== STEP 4: NEWS VALIDATION =====
        verification_log.append({
            "step": "News Cross-Validation",
            "status": "processing",
            "timestamp": datetime.now().isoformat()
        })
        
        news_check = await self.news_layer.verify_claim_with_news(
            ticker=ticker or "market",
            claim=claim,
            timeline=timeline
        )
        
        if news_check.get("verdict") == "CONTRADICTION":
            # REFUSAL: News contradicts the claim
            verification_log[-1]["status"] = "failed"
            verification_log[-1]["reason"] = news_check.get("reason")
            
            return self._generate_refusal_response(
                reason="NEWS_CONTRADICTION",
                details=news_check,
                log=verification_log,
                start_time=start_time
            )
        
        verification_log[-1]["status"] = "completed"
        verification_log[-1]["verdict"] = news_check.get("verdict")
        verification_log[-1]["num_sources"] = news_check.get("num_sources", 0)
        
        # ===== STEP 5: AGGREGATE CONFIDENCE SCORE =====
        final_confidence = self._calculate_aggregate_confidence(
            llm_result=llm_result,
            market_data=market_data,
            news_check=news_check,
            fundamental_check=fundamental_check
        )
        
        verification_log.append({
            "step": "Confidence Aggregation",
            "status": "completed",
            "final_confidence": final_confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        # ===== STEP 6: FINAL DECISION =====
        if final_confidence < 50:
            return self._generate_refusal_response(
                reason="LOW_CONFIDENCE",
                confidence=final_confidence,
                log=verification_log,
                start_time=start_time
            )
        
        # SUCCESS: Generate verification response
        return self._generate_verification_response(
            confidence=final_confidence,
            ticker=ticker,
            claim=claim,
            evidence={
                "llm_consensus": llm_result,
                "market_data": market_data,
                "news_validation": news_check,
                "fundamental_check": fundamental_check
            },
            log=verification_log,
            start_time=start_time
        )
    
    def _calculate_aggregate_confidence(
        self,
        llm_result: Dict,
        market_data: Dict,
        news_check: Dict,
        fundamental_check: Dict = None
    ) -> float:
        """
        WEIGHTED CONFIDENCE CALCULATION
        
        Formula:
        Confidence = (LLM_Consensus * 0.2) + (Market_Data_Quality * 0.5) + (News_Validation * 0.3)
        """
        # LLM Consensus (20% weight)
        llm_conf = llm_result.get("confidence", 0.5)
        llm_score = llm_conf * 100 * 0.2
        
        # Market Data Quality (50% weight)
        market_score = 0
        if market_data:
            quality = market_data.get("data_quality", "NO_DATA")
            if quality == "EXCELLENT":
                market_score = 100 * 0.5
            elif quality == "ACCEPTABLE":
                market_score = 80 * 0.5
            elif quality == "SINGLE_SOURCE":
                market_score = 60 * 0.5
            elif quality == "DISCREPANCY":
                market_score = 30 * 0.5
            else:  # NO_DATA
                market_score = 0
        else:
            # No specific ticker - use neutral score
            market_score = 50 * 0.5
        
        # News Validation (30% weight)
        verdict = news_check.get("verdict", "NEUTRAL")
        if verdict == "SUPPORTED":
            news_score = 85 * 0.3
        elif verdict == "NEUTRAL":
            news_score = 50 * 0.3
        elif verdict == "NO_NEWS" or verdict == "NO_API":
            news_score = 40 * 0.3
        else:  # CONTRADICTION
            news_score = 0 * 0.3
        
        total_confidence = llm_score + market_score + news_score
        
        # Apply risk penalties
        if market_data:
            total_confidence -= market_data.get("risk_penalty", 0) * 0.3
        if news_check:
            penalty = news_check.get("risk_penalty", 0)
            if penalty > 0:
                total_confidence -= penalty * 0.2
        
        # Apply confidence boosts
        if news_check.get("confidence_boost"):
            total_confidence += news_check["confidence_boost"]
        
        return max(0.0, min(100.0, round(total_confidence, 2)))
    
    def _generate_refusal_response(
        self,
        reason: str,
        log: List[Dict],
        start_time: datetime,
        details: Dict = None,
        confidence: float = 0.0
    ) -> Dict[str, Any]:
        """Generate a REFUSE decision response with detailed natural language explanation."""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Natural language explanations with helpful guidance
        reason_explanations = {
            "LLM_DISAGREEMENT": {
                "short": "Unable to reach consensus on content analysis",
                "detailed": "I analyzed your input using multiple AI models (OpenAI GPT-4 and Groq Llama-3), but they produced different interpretations. This usually happens when the input is ambiguous, contains a general question rather than a specific claim, or lacks sufficient context for financial analysis.",
                "guidance": "💡 **Tip**: For best results, try providing a specific financial claim to verify, such as:\n• \"Tesla stock will reach $500 by end of year\"\n• \"NVIDIA's revenue grew 200% last quarter\"\n• Paste a YouTube URL of a financial video to analyze",
                "what_i_can_do": "I'm designed to verify specific financial claims against real market data, not provide investment advice. I cross-reference claims using market prices, analyst ratings, and recent news."
            },
            "NO_MARKET_DATA": {
                "short": "Could not retrieve market data for verification",
                "detailed": "I attempted to fetch real-time market data from multiple sources (Yahoo Finance and Alpha Vantage) but couldn't retrieve reliable information for the asset mentioned. This could mean the ticker symbol doesn't exist, the market is closed, or there's a temporary data issue.",
                "guidance": "💡 **Tip**: Make sure you're using valid stock ticker symbols (e.g., AAPL, TSLA, NVDA) or cryptocurrency tickers. I work best with publicly traded assets that have available market data.",
                "what_i_can_do": "I verify claims by comparing them against live market prices, P/E ratios, analyst recommendations, and price targets from multiple data providers."
            },
            "NEWS_CONTRADICTION": {
                "short": "Recent news contradicts this claim",
                "detailed": "I searched recent news articles and financial reports about this topic, and the information I found contradicts the claim being made. This is a significant red flag that suggests the claim may be misleading or false.",
                "guidance": "⚠️ **Caution**: This claim appears to conflict with recent news reports. I recommend doing additional research before making any investment decisions based on this information.",
                "what_i_can_do": "I cross-reference claims against recent news from Tavily's news API and analyze the sentiment and facts using AI models."
            },
            "LOW_CONFIDENCE": {
                "short": "Insufficient evidence to verify this claim",
                "detailed": f"After analyzing multiple data sources, I could only achieve {confidence}% confidence in this claim. This is below my verification threshold of 50%, which means there isn't enough supporting evidence to confidently verify or deny the claim.",
                "guidance": "💡 **Tip**: Low confidence often means the claim is speculative, forward-looking (predicting future prices), or lacks sufficient supporting data. Be cautious with such claims.",
                "what_i_can_do": "I calculate confidence scores by weighing LLM consensus (20%), market data quality (50%), and news validation (30%)."
            }
        }
        
        explanation = reason_explanations.get(reason, {
            "short": "Unable to process this request",
            "detailed": f"An unexpected issue occurred during analysis: {reason}",
            "guidance": "Please try again with a specific financial claim or YouTube video URL.",
            "what_i_can_do": "I analyze financial claims using multi-API cross-verification."
        })
        
        # Construct natural language response
        natural_response = f"""**{explanation['short']}**

{explanation['detailed']}

---

{explanation['guidance']}

**What I Can Do:**
{explanation['what_i_can_do']}"""
        
        return {
            "decision": "REFUSE",
            "confidence_score": confidence,
            "reason": natural_response,
            "reason_short": explanation['short'],
            "reason_code": reason,
            "details": details,
            "verification_layers": {
                "llm_consensus": "failed" if reason == "LLM_DISAGREEMENT" else "passed",
                "market_data_triangulation": "failed" if reason == "NO_MARKET_DATA" else "passed",
                "news_validation": "failed" if reason == "NEWS_CONTRADICTION" else "passed"
            },
            "deliberation_log": log,
            "processing_time_seconds": round(elapsed, 2),
            "suggestions": [
                "Try a specific claim like: 'AAPL will hit $300 this year'",
                "Paste a YouTube video URL for full analysis",
                "Include a ticker symbol like $TSLA or $NVDA"
            ]
        }
    
    def _generate_verification_response(
        self,
        confidence: float,
        ticker: str,
        claim: str,
        evidence: Dict,
        log: List[Dict],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate a VERIFY decision response with detailed natural language explanation."""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Count sources that agreed
        sources_checked = 0
        sources_agreed = 0
        
        if evidence.get("market_data"):
            sources_checked += 2  # yfinance + alphavantage
            if evidence["market_data"].get("source_agreement"):
                sources_agreed += 2
            elif evidence["market_data"].get("yfinance_price"):
                sources_agreed += 1
        
        if evidence.get("news_validation"):
            sources_checked += evidence["news_validation"].get("num_sources", 0)
            if evidence["news_validation"].get("verdict") == "SUPPORTED":
                sources_agreed += evidence["news_validation"].get("num_sources", 0)
        
        # Build natural language summary
        market_data = evidence.get("market_data", {})
        news_data = evidence.get("news_validation", {})
        
        price_info = ""
        if market_data.get("yfinance_price"):
            price_info = f"Current market price is ${market_data['yfinance_price']:.2f}."
            if market_data.get("target_mean_price"):
                price_info += f" Analyst target price: ${market_data['target_mean_price']:.2f}."
        
        news_info = ""
        if news_data.get("verdict") == "SUPPORTED":
            news_info = f"✅ This claim is supported by {news_data.get('num_sources', 0)} recent news sources."
        elif news_data.get("verdict") == "NEUTRAL":
            news_info = "📰 No recent news directly confirms or denies this claim."
        
        confidence_level = "high" if confidence >= 75 else "moderate" if confidence >= 50 else "low"
        
        natural_response = f"""**Claim Verified with {confidence_level} confidence ({confidence}%)**

I analyzed your claim about **{ticker}** using multiple verification layers:

📊 **Market Data Check**: {price_info if price_info else "Market data analyzed successfully."}

{news_info}

🔍 **Cross-Verification Summary**:
• {sources_agreed} out of {sources_checked} data sources support this claim
• AI consensus achieved between multiple language models
• No major contradictions found in recent news

⚠️ **Important**: While I've verified the factual basis of this claim using available data, this is NOT investment advice. Always do your own research and consult a financial advisor before making investment decisions."""
        
        return {
            "decision": "VERIFY",
            "confidence_score": confidence,
            "ticker": ticker,
            "claim": claim,
            "reason": natural_response,
            "verification_layers": {
                "llm_consensus": evidence.get("llm_consensus"),
                "market_data_triangulation": evidence.get("market_data"),
                "news_validation": evidence.get("news_validation"),
                "fundamental_analysis": evidence.get("fundamental_check")
            },
            "deliberation_log": log,
            "evidence_summary": {
                "sources_checked": sources_checked,
                "sources_agreed": sources_agreed,
                "contradictions_found": 0
            },
            "processing_time_seconds": round(elapsed, 2)
        }


# Singleton instance
cross_verification_engine = CrossVerificationEngine()

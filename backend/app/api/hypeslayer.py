"""
HypeSlayer API Routes
All endpoints for the Financial Reality Check Agent
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import all HypeSlayer services
from app.hype_slayer.transcript import fetch_transcript
from app.hype_slayer.entity_parser import parse_entities
from app.hype_slayer.fact_checker import verify_claim, get_quarterly_data
from app.hype_slayer.sentiment import analyze_sentiment
from app.hype_slayer.decision_gate import calculate_confidence, make_final_decision
from app.hype_slayer.bullshit_detector import calculate_bullshit_score, quick_ticker_check, is_known_scam_pattern

router = APIRouter()


# ==================== Pydantic Models ====================

class VideoIngestRequest(BaseModel):
    video_url: str = Field(..., description="YouTube video URL")

class ParseEntitiesRequest(BaseModel):
    transcript: str = Field(..., description="Video transcript text")

class VerifyClaimRequest(BaseModel):
    ticker: str = Field(..., description="Stock/crypto ticker symbol")
    claim: str = Field(..., description="The financial claim to verify")
    claim_type: str = Field("general", description="Type: price_prediction, revenue, earnings, growth, general")

class SentimentRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for sentiment/hype")

class ConfidenceRequest(BaseModel):
    evidence_quality: float = Field(..., ge=0, le=1)
    data_completeness: float = Field(..., ge=0, le=1)
    discrepancy_score: int = Field(..., ge=0, le=100)
    hype_penalty: int = Field(..., ge=0, le=100)

class VerifyChainRequest(BaseModel):
    claim: str = Field(..., description="The claim to verify")
    ticker: str = Field(..., description="Ticker symbol")

class BullshitScoreRequest(BaseModel):
    ticker: str = Field(..., description="Ticker to check")
    claimed_price: Optional[float] = Field(None, description="Optional claimed price")

class FullAnalysisRequest(BaseModel):
    video_url: str = Field(..., description="YouTube video URL for full analysis")


# ==================== Phase 1: Data Ingestion ====================

@router.post("/ingest-video")
async def ingest_video(request: VideoIngestRequest):
    """
    Fetch and extract transcript from a YouTube video.
    """
    result = fetch_transcript(request.video_url)
    return result


@router.post("/parse-entities")
async def parse_entities_endpoint(request: ParseEntitiesRequest):
    """
    Extract financial entities (ticker, claim, timeline) from transcript.
    Implements EPISTEMIC REFUSAL if no clear ticker detected.
    """
    result = parse_entities(request.transcript)
    return result


# ==================== Phase 2: Analysis Engine ====================

@router.post("/verify-claim")
async def verify_claim_endpoint(request: VerifyClaimRequest):
    """
    Verify a financial claim against real market data from yfinance.
    """
    result = verify_claim(request.ticker, request.claim, request.claim_type)
    return result


@router.post("/analyze-sentiment")
async def analyze_sentiment_endpoint(request: SentimentRequest):
    """
    Analyze text for sentiment and hype indicators using VADER.
    Returns hype level (LOW/MEDIUM/HIGH/EXTREME) and penalty score.
    """
    result = analyze_sentiment(request.text)
    return result


@router.post("/calculate-confidence")
async def calculate_confidence_endpoint(request: ConfidenceRequest):
    """
    Calculate final confidence score and make REFUSE/VERIFY decision.
    
    Formula: Score = ((Evidence + Completeness) * 50) - (Discrepancy + Hype)
    """
    result = calculate_confidence(
        evidence_quality=request.evidence_quality,
        data_completeness=request.data_completeness,
        discrepancy_score=request.discrepancy_score,
        hype_penalty=request.hype_penalty
    )
    return result


@router.post("/verify-chain")
async def verify_chain_endpoint(request: VerifyChainRequest):
    """
    Chain of Verification (CoVe) - Generate verification questions and answers.
    """
    # Generate verification questions based on claim
    verification_questions = [
        f"What is the current market price of {request.ticker}?",
        f"What do analysts recommend for {request.ticker}?",
        f"What are the recent financial metrics for {request.ticker}?"
    ]
    
    # Answer using real data
    try:
        claim_verification = verify_claim(request.ticker, request.claim, "general")
        real_data = claim_verification.get("real_data", {})
        
        answers = [
            f"Current price: ${real_data.get('current_price', 'N/A')}",
            f"Analyst recommendation: {real_data.get('recommendation', 'N/A')} (target: ${real_data.get('target_mean_price', 'N/A')})",
            f"P/E Ratio: {real_data.get('pe_ratio', 'N/A')}, Market Cap: ${real_data.get('market_cap', 'N/A')}"
        ]
        
        # Detect discrepancies
        discrepancies = claim_verification.get("discrepancy_details", [])
        
        return {
            "verification_questions": verification_questions,
            "answers": answers,
            "discrepancies": discrepancies,
            "verification_status": claim_verification.get("verification_status"),
            "real_data_summary": real_data
        }
        
    except Exception as e:
        return {
            "verification_questions": verification_questions,
            "answers": None,
            "discrepancies": [f"Error fetching data: {str(e)}"],
            "error": str(e)
        }


# ==================== Phase 3: Monitoring & Detection ====================

@router.post("/bullshit-score")
async def bullshit_score_endpoint(request: BullshitScoreRequest):
    """
    Calculate deterministic bullshit score (NO LLM).
    Hard-coded rules for detecting obvious scams.
    """
    result = calculate_bullshit_score(request.ticker, request.claimed_price)
    return result


# ==================== Complete Pipeline ====================

@router.post("/analyze-video")
async def analyze_video_complete(request: FullAnalysisRequest):
    """
    COMPLETE PIPELINE: Orchestrates all services for full video analysis.
    This is the main endpoint for the UI.
    """
    deliberation_log = []
    
    # Step 1: Fetch transcript
    deliberation_log.append({
        "step": "INGEST",
        "status": "processing",
        "message": "Fetching video transcript...",
        "timestamp": datetime.now().isoformat()
    })
    
    transcript_result = fetch_transcript(request.video_url)
    
    if transcript_result.get("status") == "error":
        return {
            "decision": "REFUSE",
            "confidence_score": 0,
            "reason": "Failed to fetch transcript",
            "transcript": transcript_result,
            "entities": None,
            "verification": None,
            "sentiment": None,
            "deliberation_log": deliberation_log
        }
    
    deliberation_log.append({
        "step": "INGEST",
        "status": "complete",
        "message": f"Transcript fetched ({transcript_result.get('word_count', 0)} words)",
        "timestamp": datetime.now().isoformat()
    })
    
    # Step 2: Extract entities
    deliberation_log.append({
        "step": "PARSE",
        "status": "processing",
        "message": "Extracting financial entities...",
        "timestamp": datetime.now().isoformat()
    })
    
    entity_result = parse_entities(transcript_result.get("transcript", ""))
    
    deliberation_log.append({
        "step": "PARSE",
        "status": "complete",
        "message": f"Entity extraction: {entity_result.get('status')}",
        "details": {
            "asset": entity_result.get("asset"),
            "claim": entity_result.get("claim")
        },
        "timestamp": datetime.now().isoformat()
    })
    
    # Early exit if no entities found
    if entity_result.get("status") == "refused":
        return {
            "decision": "REFUSE",
            "confidence_score": 0,
            "reason": entity_result.get("refuse_reason", "Could not identify financial claim"),
            "transcript": transcript_result,
            "entities": entity_result,
            "verification": None,
            "sentiment": None,
            "deliberation_log": deliberation_log
        }
    
    # Step 3: Verify claim against real data
    ticker = entity_result.get("asset", {}).get("ticker") if entity_result.get("asset") else None
    
    if ticker:
        deliberation_log.append({
            "step": "VERIFY",
            "status": "processing",
            "message": f"Verifying claims against {ticker} market data...",
            "timestamp": datetime.now().isoformat()
        })
        
        verification_result = verify_claim(
            ticker=ticker,
            claim=entity_result.get("claim", ""),
            claim_type=entity_result.get("claim_type", "general")
        )
        
        deliberation_log.append({
            "step": "VERIFY",
            "status": "complete",
            "message": f"Verification: {verification_result.get('verification_status')}",
            "details": {
                "discrepancy_score": verification_result.get("discrepancy_score"),
                "evidence_quality": verification_result.get("evidence_quality")
            },
            "timestamp": datetime.now().isoformat()
        })
    else:
        verification_result = {
            "verification_status": "no_ticker",
            "discrepancy_score": 50,
            "evidence_quality": 0.0
        }
    
    # Step 4: Analyze sentiment/hype
    deliberation_log.append({
        "step": "SENTIMENT",
        "status": "processing",
        "message": "Analyzing sentiment and hype levels...",
        "timestamp": datetime.now().isoformat()
    })
    
    sentiment_result = analyze_sentiment(transcript_result.get("transcript", ""))
    
    deliberation_log.append({
        "step": "SENTIMENT",
        "status": "complete",
        "message": f"Hype level: {sentiment_result.get('hype_level')}",
        "details": {
            "hype_penalty": sentiment_result.get("hype_penalty"),
            "sentiment_score": sentiment_result.get("sentiment_score")
        },
        "timestamp": datetime.now().isoformat()
    })
    
    # Step 5: Make final decision
    deliberation_log.append({
        "step": "DECISION",
        "status": "processing",
        "message": "Calculating confidence score...",
        "timestamp": datetime.now().isoformat()
    })
    
    final_decision = make_final_decision(
        transcript_result=transcript_result,
        entity_result=entity_result,
        verification_result=verification_result,
        sentiment_result=sentiment_result
    )
    
    deliberation_log.append({
        "step": "DECISION",
        "status": "complete",
        "message": f"Final decision: {final_decision.get('decision')}",
        "details": {
            "confidence_score": final_decision.get("confidence_score"),
            "reasoning": final_decision.get("reasoning")
        },
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "decision": final_decision.get("decision"),
        "confidence_score": final_decision.get("confidence_score"),
        "confidence": final_decision,
        "transcript": transcript_result,
        "entities": entity_result,
        "verification": verification_result,
        "sentiment": sentiment_result,
        "deliberation_log": deliberation_log
    }


# ==================== Health Check ====================

@router.get("/health")
async def health_check():
    """
    Enhanced health check with service status.
    """
    services = {}
    
    # Check yfinance
    try:
        test = quick_ticker_check("AAPL")
        services["yfinance"] = "ok" if test.get("valid") else "degraded"
    except:
        services["yfinance"] = "error"
    
    # Check OpenAI (basic check, doesn't make API call)
    import os
    services["openai"] = "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
    
    # Check sentiment analyzer
    try:
        test_sentiment = analyze_sentiment("Test analysis")
        services["vader"] = "ok"
    except:
        services["vader"] = "error"
    
    overall_status = "ok" if all(s in ["ok", "configured"] for s in services.values()) else "degraded"
    
    return {
        "status": overall_status,
        "services": services,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0-hypeslayer"
    }

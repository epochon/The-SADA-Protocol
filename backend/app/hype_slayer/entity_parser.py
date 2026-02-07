"""
Entity Parser Service
Extracts financial entities (ticker, claim, timeline) from transcript text using LLM
"""

import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

# System prompt for entity extraction
ENTITY_EXTRACTION_PROMPT = """You are HypeSlayer, an elite financial intelligence agent.
Your mission is to analyze video transcripts to separate financial signal from noise and deception.

STEP 1: CLASSIFY TOPIC
Determine if the video is related to:
- "financial_specific": Specific Stocks/Crypto (e.g., "Buy AAPL", "BTC to 100k")
- "financial_general": General Finance/Economy (e.g., "Market Crash coming", "How to save money", "Real Estate")
- "unrelated": Non-financial content (e.g., Gaming, Cooking, Vlogs, Politics without economics)

STEP 2: EXTRACT HIGHLIGHTS
- **Suspicious Claims**: Extract specific phrases that sound like hype, guarantees ("100x soon"), fear-mongering ("Collapse imminent"), or manipulation.
- **Valid Points**: Extract sound financial advice, factual statements, or educational concepts mentioned.

STEP 3: EXTRACT ENTITIES & CLAIMS
- Identify the PRIMARY financial claim or prediction.
- If a specific asset (Stock, Crypto, ETF) is the focus, extract its ticker.

RULES:
- IF topic is "unrelated", set status="refused" and refuse_reason="Content is not financial related. Please upload a financial analysis or market news video."
- IF topic is "financial_general", you may return asset=null but must extract the primary_claim.

RESPONSE FORMAT (JSON ONLY):
{
    "video_topic": "financial_specific" | "financial_general" | "unrelated",
    "status": "success" | "refused",
    "refuse_reason": "Reason if refused",
    "asset": {"ticker": "SYMBOL" | null, "type": "stock" | "crypto" | "commodity" | "general"},
    "primary_claim": "The main prediction or thesis of the video",
    "suspicious_claims": ["exact quote 1", "exact quote 2"],
    "valid_points": ["exact quote 1", "exact quote 2"],
    "confidence": 0.0 to 1.0
}"""


def parse_entities(transcript: str) -> Dict[str, Any]:
    """
    Parse financial entities from a transcript using LLM.
    """
    if not transcript or len(transcript.strip()) < 50:
        return {
            "status": "refused",
            "video_topic": "unrelated",
            "asset": None,
            "primary_claim": None,
            "suspicious_claims": [],
            "valid_points": [],
            "confidence": 0.0,
            "refuse_reason": "Transcript too short or empty for meaningful analysis."
        }
    
    # Truncate very long transcripts to avoid token limits
    max_chars = 12000 # Increased limit for better context
    truncated = transcript[:max_chars] if len(transcript) > max_chars else transcript
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": ENTITY_EXTRACTION_PROMPT},
                {"role": "user", "content": f"Analyze this video transcript:\n\n{truncated}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return normalize_entity_response(result)
        
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Failed to parse LLM response as JSON"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Entity extraction failed: {str(e)}"
        }


def normalize_entity_response(result: Dict) -> Dict[str, Any]:
    """Normalize and validate the LLM response."""
    # Ensure lists exist
    suspicious = result.get("suspicious_claims", [])
    if isinstance(suspicious, str): suspicious = [suspicious]
    
    valid = result.get("valid_points", [])
    if isinstance(valid, str): valid = [valid]

    return {
        "status": result.get("status", "refused"),
        "video_topic": result.get("video_topic", "unrelated"),
        "asset": result.get("asset"),
        "claim": result.get("primary_claim") or result.get("claim"), # Handle potential key variations
        "suspicious_claims": suspicious,
        "valid_points": valid,
        "confidence": float(result.get("confidence", 0.0)),
        "refuse_reason": result.get("refuse_reason")
    }


def extract_ticker_simple(text: str) -> Optional[str]:
    """
    Simple regex-based ticker extraction as fallback.
    Looks for common ticker patterns like $AAPL or AAPL.
    """
    import re
    
    # Pattern for stock tickers (1-5 uppercase letters, optionally with $)
    pattern = r'\$?([A-Z]{1,5})(?:\s|$|\.|\,)'
    matches = re.findall(pattern, text)
    
    # Filter out common false positives
    common_words = {'I', 'A', 'THE', 'AND', 'OR', 'BUT', 'FOR', 'TO', 'IN', 'ON', 'AT', 'BY', 'IS', 'IT', 'AS'}
    tickers = [m for m in matches if m not in common_words and len(m) >= 2]
    
    return tickers[0] if tickers else None

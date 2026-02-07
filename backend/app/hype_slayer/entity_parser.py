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
ENTITY_EXTRACTION_PROMPT = """You are a financial entity extraction AI. Your job is to analyze video transcripts and extract:

1. **Asset**: The stock ticker or cryptocurrency being discussed (e.g., "GME", "BTC", "AAPL")
2. **Claim**: The specific financial claim or prediction being made
3. **Timeline**: When the claim is expected to materialize (if mentioned)
4. **Claim Type**: One of: "price_prediction", "revenue", "earnings", "growth", "general"

RULES:
- If you cannot clearly identify a specific ticker symbol, return status "refused"
- Be skeptical of vague claims - extract only concrete, verifiable statements
- If multiple assets are mentioned, focus on the PRIMARY one being discussed
- Timeline should be normalized (e.g., "next week", "by Q4 2024", "within 6 months")

Respond ONLY with valid JSON in this exact format:
{
    "status": "success" | "refused",
    "asset": {"type": "stock" | "crypto" | "index", "ticker": "SYMBOL"},
    "claim": "The specific claim extracted",
    "claim_type": "price_prediction" | "revenue" | "earnings" | "growth" | "general",
    "timeline": "Timeframe if mentioned, else null",
    "confidence": 0.0 to 1.0,
    "refuse_reason": "Reason if status is refused, else null"
}"""


def parse_entities(transcript: str) -> Dict[str, Any]:
    """
    Parse financial entities from a transcript using LLM.
    
    Args:
        transcript: The full transcript text
        
    Returns:
        dict: Extracted entities with status
    """
    if not transcript or len(transcript.strip()) < 50:
        return {
            "status": "refused",
            "asset": None,
            "claim": None,
            "claim_type": None,
            "timeline": None,
            "confidence": 0.0,
            "refuse_reason": "Transcript too short or empty for meaningful analysis."
        }
    

    # Truncate very long transcripts to avoid token limits
    max_chars = 8000
    truncated = transcript[:max_chars] if len(transcript) > max_chars else transcript
    
    # Priority 1: OpenAI (Best Quality)
    if os.getenv("OPENAI_API_KEY"):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": ENTITY_EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Analyze this video transcript and extract financial entities:\n\n{truncated}"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return normalize_entity_response(result)
            
        except json.JSONDecodeError:
            return {"status": "error", "error": "Failed to parse LLM response as JSON"}
        except Exception as e:
            # If OpenAI fails, fall through to fallback? No, error out if key was provided but call failed.
            return {"status": "error", "error": f"OpenAI extraction failed: {str(e)}"}

    # Priority 2: Groq (Free Tier / Llama 3)
    else:
        print("ℹ️ OpenAI Key missing. Attempting fallback to Groq (Llama 3)...")
        try:
            # Lazy import to avoid crash if GROQ_API_KEY is missing (HypeSlayerLLM init checks key)
            from app.agent.hypeslayer_llm import hypeslayer_llm
            
            groq_result = hypeslayer_llm.extract_entities(truncated)
            
            # Map ExtractedEntity to HypeSlayer dict format
            status = "refused" if not groq_result.ticker else "success"
            normalized = {
                "status": status,
                "asset": {"type": groq_result.asset_type, "ticker": groq_result.ticker} if groq_result.ticker else None,
                "claim": groq_result.claim,
                "claim_type": "general", # Groq module doesn't extract type yet
                "timeline": groq_result.timeline,
                "confidence": groq_result.confidence,
                "refuse_reason": groq_result.refusal_reason
            }
            return normalized
            
        except ImportError:
            return {"status": "error", "error": "Groq module dependencies missing."}
        except ValueError as ve:
            return {
                "status": "error", 
                "error": "Missing API Keys. Please provide OPENAI_API_KEY (Recommended) or GROQ_API_KEY (Free)."
            }
        except Exception as e:
            return {"status": "error", "error": f"Groq extraction failed: {str(e)}"}


def normalize_entity_response(result: Dict) -> Dict[str, Any]:
    """Normalize and validate the LLM response."""
    return {
        "status": result.get("status", "refused"),
        "asset": result.get("asset"),
        "claim": result.get("claim"),
        "claim_type": result.get("claim_type", "general"),
        "timeline": result.get("timeline"),
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

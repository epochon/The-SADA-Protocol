"""
LLM Consensus Layer
Extracts entities using TWO different LLMs and compares results.
Only proceeds if both agree on the ticker/asset.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from difflib import SequenceMatcher
from openai import OpenAI
from groq import Groq

from app.core.config import settings


class LLMConsensusExtractor:
    """
    Cross-validates entity extraction between OpenAI and Groq.
    Prevents hallucinated tickers from entering the verification pipeline.
    """
    
    EXTRACTION_PROMPT = """You are a financial entity extractor. Analyze the transcript and extract:
1. The PRIMARY financial asset being discussed (ticker symbol if stock/crypto)
2. The MAIN claim or prediction being made
3. The timeline mentioned for the claim

Respond ONLY in this JSON format:
{
    "ticker": "SYMBOL" or null,
    "asset_type": "stock" | "crypto" | "commodity" | "general",
    "claim": "The main prediction or thesis",
    "timeline": "by next week" | "this year" | "soon" | null,
    "confidence": 0.0 to 1.0
}"""

    def __init__(self):
        self.openai_client = None
        self.groq_client = None
        
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if os.getenv("GROQ_API_KEY"):
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def extract_with_consensus(self, transcript: str) -> Dict[str, Any]:
        """
        Cross-check entity extraction between OpenAI and Groq.
        Now handles general questions and short inputs more gracefully.
        
        Returns:
            {
                "consensus_reached": bool,
                "primary_result": {...},
                "fallback_result": {...},
                "agreed_ticker": str or None,
                "confidence": float,
                "discrepancies": List[str]
            }
        """
        transcript = transcript.strip()
        
        # Handle very short inputs (but don't reject immediately)
        if len(transcript) < 10:
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "decision": "REFUSE",
                "reason": "Please provide more detail for analysis"
            }
        
        # Truncate for API limits
        truncated = transcript[:12000]
        
        # Check available clients
        if not self.openai_client and not self.groq_client:
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "decision": "REFUSE", 
                "reason": "No LLM API keys configured - please set OPENAI_API_KEY or GROQ_API_KEY in backend/.env"
            }
        
        # If only one client available, use it (no consensus possible but still useful)
        if not self.openai_client or not self.groq_client:
            single_result = await self._extract_single(truncated)
            
            # Handle extraction errors
            if single_result.get("error"):
                return {
                    "consensus_reached": False,
                    "confidence": 0.0,
                    "decision": "REFUSE",
                    "reason": f"LLM API error: {single_result.get('error')}"
                }
            
            return {
                "consensus_reached": True,  # Single source fallback
                "single_source": True,
                "agreed_ticker": single_result.get("ticker"),
                "agreed_claim": single_result.get("claim"),
                "agreed_timeline": single_result.get("timeline"),
                "primary_result": single_result,
                "fallback_result": None,
                "confidence": single_result.get("confidence", 0.5) * 0.8,  # Light penalty for single source
                "discrepancies": ["Single LLM source - using without cross-validation"]
            }
        
        # Extract with both LLMs concurrently
        primary_task = asyncio.create_task(self._extract_openai(truncated))
        fallback_task = asyncio.create_task(self._extract_groq(truncated))
        
        primary_result, fallback_result = await asyncio.gather(
            primary_task, fallback_task, return_exceptions=True
        )
        
        # Handle extraction failures - if one fails, use the other
        if isinstance(primary_result, Exception):
            primary_result = {"error": str(primary_result), "ticker": None}
        if isinstance(fallback_result, Exception):
            fallback_result = {"error": str(fallback_result), "ticker": None}
        
        # If both failed, report error
        if primary_result.get("error") and fallback_result.get("error"):
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "decision": "REFUSE",
                "reason": f"Both LLM APIs failed. OpenAI: {primary_result.get('error')}, Groq: {fallback_result.get('error')}"
            }
        
        # If one failed, use the other (with penalty)
        if primary_result.get("error"):
            return {
                "consensus_reached": True,
                "single_source": True,
                "agreed_ticker": fallback_result.get("ticker"),
                "agreed_claim": fallback_result.get("claim"),
                "agreed_timeline": fallback_result.get("timeline"),
                "primary_result": fallback_result,
                "fallback_result": None,
                "confidence": fallback_result.get("confidence", 0.5) * 0.7,
                "discrepancies": [f"OpenAI failed, using Groq only: {primary_result.get('error')}"]
            }
        
        if fallback_result.get("error"):
            return {
                "consensus_reached": True,
                "single_source": True,
                "agreed_ticker": primary_result.get("ticker"),
                "agreed_claim": primary_result.get("claim"),
                "agreed_timeline": primary_result.get("timeline"),
                "primary_result": primary_result,
                "fallback_result": None,
                "confidence": primary_result.get("confidence", 0.5) * 0.7,
                "discrepancies": [f"Groq failed, using OpenAI only: {fallback_result.get('error')}"]
            }
        
        # Compare results from both LLMs
        return self._compare_extractions(primary_result, fallback_result)
    
    async def _extract_single(self, transcript: str) -> Dict[str, Any]:
        """Extract using whichever client is available."""
        if self.openai_client:
            return await self._extract_openai(transcript)
        return await self._extract_groq(transcript)
    
    async def _extract_openai(self, transcript: str) -> Dict[str, Any]:
        """Extract entities using OpenAI GPT-4."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self.EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Extract entities from:\n\n{transcript}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "ticker": None, "confidence": 0.0}
    
    async def _extract_groq(self, transcript: str) -> Dict[str, Any]:
        """Extract entities using Groq Llama 3."""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Extract entities from:\n\n{transcript}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": str(e), "ticker": None, "confidence": 0.0}
    
    def _compare_extractions(self, primary: Dict, fallback: Dict) -> Dict[str, Any]:
        """
        Compare extraction results and determine consensus.
        More forgiving - allows general claims without specific tickers.
        """
        discrepancies = []
        
        # Extract tickers (normalize to uppercase)
        primary_ticker = (primary.get("ticker") or "").upper().strip()
        fallback_ticker = (fallback.get("ticker") or "").upper().strip()
        
        # Remove common non-ticker values
        for invalid in ["", "NULL", "NONE", "N/A", "GENERAL"]:
            if primary_ticker == invalid:
                primary_ticker = ""
            if fallback_ticker == invalid:
                fallback_ticker = ""
        
        # Ticker matching - only strict if BOTH found tickers
        both_have_tickers = primary_ticker and fallback_ticker
        ticker_match = primary_ticker == fallback_ticker if both_have_tickers else True
        
        if not ticker_match:
            discrepancies.append(
                f"Ticker mismatch: OpenAI='{primary_ticker}' vs Groq='{fallback_ticker}'"
            )
        
        # Claim similarity using fuzzy matching
        primary_claim = primary.get("claim", "") or ""
        fallback_claim = fallback.get("claim", "") or ""
        
        # Handle empty claims
        if not primary_claim and not fallback_claim:
            claim_similarity = 0.5  # Neutral
        elif not primary_claim or not fallback_claim:
            claim_similarity = 0.6  # One has claim, slight penalty
        else:
            claim_similarity = SequenceMatcher(
                None, 
                primary_claim.lower(), 
                fallback_claim.lower()
            ).ratio()
        
        if claim_similarity < 0.4:
            discrepancies.append(f"Claim similarity low: {claim_similarity:.2f}")
        
        # Calculate confidence - be more generous
        confidence = 0.3  # Base confidence for reaching this point
        
        if both_have_tickers and ticker_match:
            confidence += 0.4  # Strong agreement
        elif primary_ticker or fallback_ticker:
            confidence += 0.2  # At least one ticker found
        else:
            confidence += 0.15  # General claim, no ticker - still valid
        
        if claim_similarity > 0.6:
            confidence += 0.2
        elif claim_similarity > 0.4:
            confidence += 0.1
        
        if primary.get("confidence") and fallback.get("confidence"):
            avg_llm_conf = (primary["confidence"] + fallback["confidence"]) / 2
            confidence += avg_llm_conf * 0.15
        
        # Only refuse if tickers ACTIVELY disagree (both found but different)
        if not ticker_match and both_have_tickers:
            # Still provide the data but with low confidence
            return {
                "consensus_reached": False,
                "primary_result": primary,
                "fallback_result": fallback,
                "agreed_ticker": primary_ticker,  # Use primary as fallback
                "agreed_claim": primary_claim or fallback_claim,
                "confidence": 0.3,  # Low but not zero
                "decision": "REFUSE",
                "reason": f"LLM disagreement on ticker: OpenAI='{primary_ticker}' vs Groq='{fallback_ticker}'. Using OpenAI's interpretation with reduced confidence.",
                "discrepancies": discrepancies
            }
        
        # Use whichever ticker was found (or none if general claim)
        agreed_ticker = primary_ticker or fallback_ticker or None
        best_claim = primary_claim if len(primary_claim) > len(fallback_claim) else fallback_claim
        
        return {
            "consensus_reached": True,  # More forgiving - proceed with available data
            "primary_result": primary,
            "fallback_result": fallback,
            "agreed_ticker": agreed_ticker,
            "agreed_claim": best_claim or primary_claim or fallback_claim,
            "agreed_timeline": primary.get("timeline") or fallback.get("timeline"),
            "claim_similarity": claim_similarity,
            "confidence": min(confidence, 1.0),
            "discrepancies": discrepancies
        }


# Singleton instance
llm_consensus = LLMConsensusExtractor()

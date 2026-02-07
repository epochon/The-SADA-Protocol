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
        if len(transcript.strip()) < 50:
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "decision": "REFUSE",
                "reason": "Transcript too short for meaningful analysis"
            }
        
        # Truncate for API limits
        truncated = transcript[:12000]
        
        # Check available clients
        if not self.openai_client and not self.groq_client:
            return {
                "consensus_reached": False,
                "confidence": 0.0,
                "decision": "REFUSE",
                "reason": "No LLM API keys configured"
            }
        
        # If only one client available, use it (no consensus possible)
        if not self.openai_client or not self.groq_client:
            single_result = await self._extract_single(truncated)
            return {
                "consensus_reached": True,  # Single source fallback
                "single_source": True,
                "agreed_ticker": single_result.get("ticker"),
                "primary_result": single_result,
                "fallback_result": None,
                "confidence": single_result.get("confidence", 0.5) * 0.7,  # Penalize single source
                "discrepancies": ["Single LLM source - no cross-validation possible"]
            }
        
        # Extract with both LLMs concurrently
        primary_task = asyncio.create_task(self._extract_openai(truncated))
        fallback_task = asyncio.create_task(self._extract_groq(truncated))
        
        primary_result, fallback_result = await asyncio.gather(
            primary_task, fallback_task, return_exceptions=True
        )
        
        # Handle extraction failures
        if isinstance(primary_result, Exception):
            primary_result = {"error": str(primary_result), "ticker": None}
        if isinstance(fallback_result, Exception):
            fallback_result = {"error": str(fallback_result), "ticker": None}
        
        # Compare results
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
        """
        discrepancies = []
        
        # Extract tickers (normalize to uppercase)
        primary_ticker = (primary.get("ticker") or "").upper().strip()
        fallback_ticker = (fallback.get("ticker") or "").upper().strip()
        
        # Ticker matching
        ticker_match = primary_ticker == fallback_ticker
        
        if not ticker_match and primary_ticker and fallback_ticker:
            discrepancies.append(
                f"Ticker mismatch: OpenAI='{primary_ticker}' vs Groq='{fallback_ticker}'"
            )
        
        # Claim similarity using fuzzy matching
        primary_claim = primary.get("claim", "") or ""
        fallback_claim = fallback.get("claim", "") or ""
        claim_similarity = SequenceMatcher(
            None, 
            primary_claim.lower(), 
            fallback_claim.lower()
        ).ratio()
        
        if claim_similarity < 0.5:
            discrepancies.append(f"Claim similarity low: {claim_similarity:.2f}")
        
        # Calculate confidence
        confidence = 0.0
        if ticker_match and primary_ticker:
            confidence += 0.5
        if claim_similarity > 0.7:
            confidence += 0.3
        if primary.get("confidence") and fallback.get("confidence"):
            avg_llm_conf = (primary["confidence"] + fallback["confidence"]) / 2
            confidence += avg_llm_conf * 0.2
        
        # CRITICAL: If tickers don't match, REFUSE
        if not ticker_match and primary_ticker and fallback_ticker:
            return {
                "consensus_reached": False,
                "primary_result": primary,
                "fallback_result": fallback,
                "agreed_ticker": None,
                "confidence": 0.0,
                "decision": "REFUSE",
                "reason": f"LLM disagreement: OpenAI detected '{primary_ticker}' but Groq detected '{fallback_ticker}'",
                "discrepancies": discrepancies
            }
        
        # Use whichever ticker was found
        agreed_ticker = primary_ticker or fallback_ticker or None
        
        return {
            "consensus_reached": ticker_match or bool(agreed_ticker),
            "primary_result": primary,
            "fallback_result": fallback,
            "agreed_ticker": agreed_ticker,
            "agreed_claim": primary_claim or fallback_claim,
            "agreed_timeline": primary.get("timeline") or fallback.get("timeline"),
            "claim_similarity": claim_similarity,
            "confidence": confidence,
            "discrepancies": discrepancies
        }


# Singleton instance
llm_consensus = LLMConsensusExtractor()

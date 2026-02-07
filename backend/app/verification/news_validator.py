"""
News Validation Layer
Uses Tavily to search for recent news about the ticker.
Cross-checks if video claims align with verified news sources.
"""

import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

from app.core.config import settings


class NewsValidationLayer:
    """
    Searches Tavily for recent news and uses OpenAI to analyze
    if news supports or contradicts the video claim.
    """
    
    NEWS_ANALYSIS_PROMPT = """Analyze if the following news articles support, contradict, or are neutral about this claim.

CLAIM: "{claim}"

NEWS ARTICLES:
{news_text}

Respond ONLY in this JSON format:
{{
    "supports_claim": boolean,
    "contradicts_claim": boolean,
    "neutral": boolean,
    "explanation": "brief explanation of your verdict",
    "key_facts": ["fact 1", "fact 2"],
    "contradiction_details": "details if contradicts, else null"
}}"""

    def __init__(self):
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.openai_client = None
        
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def verify_claim_with_news(
        self,
        ticker: str,
        claim: str,
        timeline: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for recent news about the ticker and validate the claim.
        
        Returns:
            {
                "news_found": bool,
                "verdict": "SUPPORTED" | "CONTRADICTION" | "NEUTRAL" | "NO_NEWS",
                "num_sources": int,
                "sources": List[Dict],
                "risk_penalty": int,
                "confidence_boost": int
            }
        """
        # Check if Tavily is configured
        if not self.tavily_key:
            return {
                "news_found": False,
                "verdict": "NO_API",
                "num_sources": 0,
                "risk_penalty": 20,
                "reason": "Tavily API key not configured - skipping news validation"
            }
        
        # Search Tavily for recent news
        search_query = f"{ticker} stock {claim[:50]} latest news"
        news_results = await self._search_tavily(search_query)
        
        if not news_results or len(news_results) == 0:
            return {
                "news_found": False,
                "verdict": "NO_NEWS",
                "num_sources": 0,
                "risk_penalty": 20,
                "reason": "No recent news found related to this claim"
            }
        
        # Analyze news sentiment and fact-check using OpenAI
        if not self.openai_client:
            # Can't analyze without OpenAI - just report news found
            return {
                "news_found": True,
                "verdict": "NEUTRAL",
                "num_sources": len(news_results),
                "sources": news_results[:3],
                "risk_penalty": 10,
                "reason": "News found but no LLM available for analysis"
            }
        
        # Use OpenAI to analyze claim vs news
        news_analysis = await self._analyze_news_articles(news_results, claim)
        
        # Determine verdict
        if news_analysis.get("contradicts_claim"):
            return {
                "news_found": True,
                "verdict": "CONTRADICTION",
                "num_sources": len(news_results),
                "sources": news_results[:3],
                "analysis": news_analysis,
                "risk_penalty": 60,
                "confidence_boost": 0,
                "reason": f"News contradicts claim: {news_analysis.get('contradiction_details', 'See analysis')}"
            }
        
        if news_analysis.get("supports_claim"):
            return {
                "news_found": True,
                "verdict": "SUPPORTED",
                "num_sources": len(news_results),
                "sources": news_results[:3],
                "analysis": news_analysis,
                "risk_penalty": -10,  # Actually reduces risk!
                "confidence_boost": 15,
                "reason": news_analysis.get("explanation", "News supports claim")
            }
        
        # Neutral
        return {
            "news_found": True,
            "verdict": "NEUTRAL",
            "num_sources": len(news_results),
            "sources": news_results[:3],
            "analysis": news_analysis,
            "risk_penalty": 10,
            "confidence_boost": 0,
            "reason": "News exists but doesn't clearly support or contradict"
        }
    
    async def _search_tavily(self, query: str) -> List[Dict[str, Any]]:
        """Search Tavily for recent news articles."""
        try:
            import requests
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_key,
                "query": query,
                "search_depth": "basic",
                "include_domains": [
                    "reuters.com", "bloomberg.com", "wsj.com", 
                    "cnbc.com", "marketwatch.com", "seekingalpha.com",
                    "finance.yahoo.com", "investing.com"
                ],
                "max_results": 5
            }
            
            response = requests.post(url, json=payload, timeout=15)
            data = response.json()
            
            results = data.get("results", [])
            
            # Format results
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:500],
                    "score": r.get("score", 0)
                })
            
            return formatted
            
        except Exception as e:
            print(f"⚠️ Tavily search error: {e}")
            return []
    
    async def _analyze_news_articles(
        self,
        news_results: List[Dict],
        original_claim: str
    ) -> Dict[str, Any]:
        """Use OpenAI to analyze if news supports/contradicts the claim."""
        try:
            # Prepare news text
            news_text = "\n\n".join([
                f"Source: {article['title']}\n{article['snippet']}"
                for article in news_results[:5]
            ])
            
            prompt = self.NEWS_ANALYSIS_PROMPT.format(
                claim=original_claim,
                news_text=news_text
            )
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a financial news analyst. Analyze claim validity based on news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"⚠️ News analysis error: {e}")
            return {
                "supports_claim": False,
                "contradicts_claim": False,
                "neutral": True,
                "explanation": f"Analysis error: {str(e)}"
            }


# Singleton instance
news_validator = NewsValidationLayer()

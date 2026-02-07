"""
HypeSlayer Agent - LangChain Integration with Groq
Uses Groq's ultra-fast Llama 3 for entity extraction and claim analysis
FREE and 10x faster than OpenAI!
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional, Literal

class ExtractedEntity(BaseModel):
    """Structured output for entity extraction"""
    asset_type: Optional[Literal["stock", "crypto", "commodity", "unknown"]] = Field(description="Type of financial asset")
    ticker: Optional[str] = Field(description="Stock ticker or crypto symbol (e.g., GME, BTC)")
    claim: Optional[str] = Field(description="Main financial claim or prediction")
    timeline: Optional[str] = Field(description="When the claim is expected to happen")
    confidence: float = Field(description="Confidence in extraction (0-1)")
    refusal_reason: Optional[str] = Field(description="Reason for refusal if ticker unclear")

class HypeSlayerLLM:
    """LangChain wrapper for HypeSlayer analysis using Groq"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment. Get free key from console.groq.com")
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",  # Fast and accurate
            temperature=0.1,  # Low temperature for factual extraction
            api_key=api_key
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ExtractedEntity)
    
    def extract_entities(self, transcript: str) -> ExtractedEntity:
        """
        Extract financial entities from video transcript
        Implements Epistemic Refusal if ticker is unclear
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial entity extraction expert for the HypeSlayer system.
Your job is to extract:
1. Asset type (stock/crypto/commodity)
2. Ticker symbol (e.g., GME, TSLA, BTC)
3. Main financial claim or prediction
4. Timeline for the claim

CRITICAL RULES:
- If NO clear ticker is mentioned, set ticker=null and provide refusal_reason
- Only extract EXPLICIT claims, not implied ones
- Be conservative - when in doubt, refuse
- Confidence should reflect clarity of information

{format_instructions}
"""),
            ("user", "Transcript:\n{transcript}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "transcript": transcript,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            # Fallback to refusal on parsing errors
            return ExtractedEntity(
                asset_type="unknown",
                ticker=None,
                claim=None,
                timeline=None,
                confidence=0.0,
                refusal_reason=f"Extraction failed: {str(e)}"
            )
    
    def generate_verification_questions(self, claim: str, ticker: str) -> list[str]:
        """
        Generate Chain of Verification (CoVe) questions
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a skeptical financial analyst.
Generate 3 specific verification questions to fact-check the claim.
Questions should be answerable with market data (price, revenue, earnings, etc.)

Return ONLY a JSON array of 3 questions, nothing else.
Example: ["What is the current P/E ratio?", "What was Q3 revenue?", "What is analyst consensus?"]
"""),
            ("user", "Claim: {claim}\nTicker: {ticker}")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({"claim": claim, "ticker": ticker})
            # Parse JSON array from response
            import json
            questions = json.loads(response.content)
            return questions[:3]  # Ensure max 3 questions
        except:
            # Fallback questions
            return [
                f"What is the current price of {ticker}?",
                f"What is the latest quarterly revenue for {ticker}?",
                f"What is the analyst consensus rating for {ticker}?"
            ]

# Singleton instance
hypeslayer_llm = HypeSlayerLLM()

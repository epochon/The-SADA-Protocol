"""
Hype Detector / Sentiment Analysis Service
Uses VADER for sentiment analysis and hype level classification
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any, List
import re


# Initialize VADER analyzer
analyzer = SentimentIntensityAnalyzer()

# Financial hype indicators - words that indicate potential pump/hype
HYPE_INDICATORS = {
    "extreme": [
        "guaranteed", "100%", "can't lose", "free money", "get rich quick",
        "to the moon", "rocket", "🚀", "explode", "lambo", "millionaire",
        "once in a lifetime", "next bitcoin", "10x", "100x", "1000x"
    ],
    "high": [
        "massive gains", "huge opportunity", "don't miss", "act now", 
        "limited time", "insider", "secret", "they don't want you to know",
        "undervalued gem", "sleeping giant", "about to blow up"
    ],
    "medium": [
        "bullish", "buy now", "strong buy", "amazing", "incredible",
        "game changer", "revolutionary", "disruptive"
    ]
}

# Red flag patterns
RED_FLAGS = [
    r"financial advice",  # Disclaimer dodge pattern
    r"not a financial advisor",
    r"do your own research",  # Often precedes bad advice
    r"trust me",
    r"i\'m telling you",
]


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment and hype level of text.
    
    Args:
        text: Text to analyze (transcript or claim)
        
    Returns:
        dict: Sentiment analysis with hype scoring
    """
    if not text or len(text.strip()) < 10:
        return {
            "sentiment_score": 0.0,
            "hype_level": "UNKNOWN",
            "hype_penalty": 0,
            "emotional_intensity": "none",
            "error": "Text too short for analysis"
        }
    
    # VADER sentiment analysis
    vader_scores = analyzer.polarity_scores(text)
    compound = vader_scores['compound']
    
    # Calculate hype indicators
    hype_result = detect_hype_indicators(text)
    
    # Detect red flags
    red_flags = detect_red_flags(text)
    
    # Calculate emotional intensity
    emotional_intensity = calculate_emotional_intensity(vader_scores, text)
    
    # Calculate hype penalty
    hype_penalty = calculate_hype_penalty(
        sentiment_compound=compound,
        hype_count=hype_result["total_count"],
        red_flag_count=len(red_flags),
        emotional_intensity=emotional_intensity
    )
    
    # Classify hype level
    hype_level = classify_hype_level(compound, hype_result["total_count"], hype_penalty)
    
    return {
        "sentiment_score": round(compound, 3),
        "sentiment_breakdown": {
            "positive": vader_scores['pos'],
            "negative": vader_scores['neg'],
            "neutral": vader_scores['neu']
        },
        "hype_level": hype_level,
        "hype_indicators_found": hype_result["indicators"],
        "hype_indicator_count": hype_result["total_count"],
        "red_flags": red_flags,
        "emotional_intensity": emotional_intensity,
        "hype_penalty": hype_penalty,
        "suspicion_flag": compound > 0.8 or hype_penalty > 40
    }


def detect_hype_indicators(text: str) -> Dict[str, Any]:
    """Detect hype indicator phrases in text."""
    text_lower = text.lower()
    found = {"extreme": [], "high": [], "medium": []}
    
    for level, indicators in HYPE_INDICATORS.items():
        for indicator in indicators:
            if indicator.lower() in text_lower:
                found[level].append(indicator)
    
    total = len(found["extreme"]) * 3 + len(found["high"]) * 2 + len(found["medium"])
    
    return {
        "indicators": found,
        "total_count": total,
        "extreme_count": len(found["extreme"]),
        "high_count": len(found["high"]),
        "medium_count": len(found["medium"])
    }


def detect_red_flags(text: str) -> List[str]:
    """Detect red flag patterns in text."""
    text_lower = text.lower()
    flags = []
    
    for pattern in RED_FLAGS:
        if re.search(pattern, text_lower):
            flags.append(pattern)
    
    return flags


def calculate_emotional_intensity(vader_scores: Dict, text: str) -> str:
    """Calculate emotional intensity level."""
    # Check for exclamation marks and caps
    exclaim_count = text.count('!')
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    
    # High positive or negative sentiment with markers
    compound = abs(vader_scores['compound'])
    
    if compound > 0.8 or exclaim_count > 5 or caps_ratio > 0.3:
        return "extreme"
    elif compound > 0.5 or exclaim_count > 2 or caps_ratio > 0.15:
        return "high"
    elif compound > 0.2:
        return "medium"
    else:
        return "low"


def calculate_hype_penalty(
    sentiment_compound: float,
    hype_count: int,
    red_flag_count: int,
    emotional_intensity: str
) -> int:
    """
    Calculate hype penalty score (0-100).
    Higher = more suspicious/hyped content.
    """
    penalty = 0
    
    # Overly positive sentiment penalty
    if sentiment_compound > 0.8:
        penalty += 25
    elif sentiment_compound > 0.6:
        penalty += 15
    elif sentiment_compound > 0.4:
        penalty += 5
    
    # Hype indicator penalty
    penalty += min(hype_count * 5, 40)  # Cap at 40
    
    # Red flag penalty
    penalty += red_flag_count * 8
    
    # Emotional intensity penalty
    intensity_penalty = {"extreme": 20, "high": 10, "medium": 5, "low": 0}
    penalty += intensity_penalty.get(emotional_intensity, 0)
    
    return min(penalty, 100)


def classify_hype_level(compound: float, hype_count: int, penalty: int) -> str:
    """Classify overall hype level."""
    if penalty >= 60 or hype_count >= 5:
        return "EXTREME"
    elif penalty >= 40 or hype_count >= 3:
        return "HIGH"
    elif penalty >= 20 or hype_count >= 1:
        return "MEDIUM"
    else:
        return "LOW"

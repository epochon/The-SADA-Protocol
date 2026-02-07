"""
Risk Profile Assessment Module

This module implements a psychometric questionnaire to assess user's
financial risk tolerance and investment behavior patterns.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class RiskCategory(str, Enum):
    """Risk tolerance categories"""
    CONSERVATIVE = "Conservative"
    MODERATE = "Moderate"
    AGGRESSIVE = "Aggressive"


class QuestionnaireAnswer(BaseModel):
    """Single answer to a questionnaire question"""
    question_id: str
    answer: str  # A, B, or C
    points: int = Field(ge=1, le=3)  # 1=Conservative, 2=Moderate, 3=Aggressive


class RiskProfile(BaseModel):
    """Complete user risk profile"""
    total_score: int = Field(ge=7, le=27)
    category: RiskCategory
    answers: Dict[str, str]
    constraints: List[str]
    recommendations: List[str]
    completed_at: str


class RiskProfileCalculator:
    """
    Calculates risk profile based on questionnaire responses
    
    Scoring:
    - A answers = 1 point (Conservative)
    - B answers = 2 points (Moderate)
    - C answers = 3 points (Aggressive)
    
    Total Score Mapping:
    - 7-13: Conservative
    - 14-22: Moderate
    - 23-27: Aggressive
    """
    
    # Point mapping for each answer
    ANSWER_POINTS = {
        "A": 1,
        "B": 2,
        "C": 3
    }
    
    # Questions structure (will be populated from uploaded file)
    QUESTIONS = {
        "Q1": {
            "category": "Financial Stability",
            "text": "How stable is your income?",
            "options": {
                "A": "Very stable (salaried, government job)",
                "B": "Somewhat stable (regular business income)",
                "C": "Unpredictable (freelance, commission-based)"
            }
        },
        "Q2": {
            "category": "Financial Stability",
            "text": "Do you have insurance and 3-6 months emergency fund?",
            "options": {
                "A": "Yes, fully covered",
                "B": "Partially covered",
                "C": "No, not yet"
            }
        },
        "Q3": {
            "category": "Goals & Time Horizon",
            "text": "What is your primary investment objective?",
            "options": {
                "A": "Capital protection (preserve wealth)",
                "B": "Balanced growth (moderate returns)",
                "C": "Maximum growth (aggressive returns)"
            }
        },
        "Q4": {
            "category": "Experience",
            "text": "How familiar are you with financial markets?",
            "options": {
                "A": "Beginner (just starting)",
                "B": "Some experience (1-3 years)",
                "C": "Comfortable (3+ years, understand volatility)"
            }
        },
        "Q5": {
            "category": "Volatility Tolerance",
            "text": "What's the maximum drop you can tolerate?",
            "options": {
                "A": "5-10% (very low tolerance)",
                "B": "10-25% (moderate tolerance)",
                "C": "25-40% (high tolerance)"
            }
        },
        "Q6": {
            "category": "Volatility Tolerance",
            "text": "How long can you stay invested if value drops?",
            "options": {
                "A": "Less than 1 year",
                "B": "1-3 years",
                "C": "3-5+ years (long-term horizon)"
            }
        },
        "Q7": {
            "category": "Volatility Tolerance",
            "text": "How would you feel during a market crash?",
            "options": {
                "A": "Very stressed, would lose sleep",
                "B": "Stressed but manageable",
                "C": "Comfortable, see it as opportunity"
            }
        },
        "Q8": {
            "category": "Behavior in Downturns",
            "text": "What would you do if your investment fell 20%?",
            "options": {
                "A": "Sell immediately to prevent further loss",
                "B": "Hold and wait for recovery",
                "C": "Buy more (averaging down)"
            }
        },
        "Q9": {
            "category": "Behavior in Downturns",
            "text": "If your SIP is down, would you continue?",
            "options": {
                "A": "Stop SIP immediately",
                "B": "Continue with discomfort",
                "C": "Continue confidently (rupee cost averaging)"
            }
        }
    }
    
    @classmethod
    def calculate_score(cls, answers: Dict[str, str]) -> int:
        """Calculate total score from answers"""
        total = 0
        for question_id, answer in answers.items():
            if answer in cls.ANSWER_POINTS:
                total += cls.ANSWER_POINTS[answer]
        return total
    
    @classmethod
    def determine_category(cls, score: int) -> RiskCategory:
        """Determine risk category from total score"""
        if score <= 13:
            return RiskCategory.CONSERVATIVE
        elif score <= 22:
            return RiskCategory.MODERATE
        else:
            return RiskCategory.AGGRESSIVE
    
    @classmethod
    def generate_constraints(cls, category: RiskCategory, answers: Dict[str, str]) -> List[str]:
        """Generate investment constraints based on profile"""
        constraints = []
        
        if category == RiskCategory.CONSERVATIVE:
            constraints.extend([
                "avoid_crypto",
                "avoid_microcap_stocks",
                "avoid_options_derivatives",
                "max_drawdown_10pct",
                "prefer_debt_instruments"
            ])
            
            # Additional constraints based on specific answers
            if answers.get("Q5") == "A":
                constraints.append("very_low_volatility_only")
            if answers.get("Q6") == "A":
                constraints.append("short_term_horizon_only")
                
        elif category == RiskCategory.MODERATE:
            constraints.extend([
                "avoid_meme_coins",
                "avoid_penny_stocks",
                "max_drawdown_25pct",
                "balanced_portfolio_required"
            ])
            
        else:  # AGGRESSIVE
            constraints.extend([
                "verify_scams_only",  # Don't lecture on volatility
                "focus_on_accuracy_not_risk"
            ])
        
        return constraints
    
    @classmethod
    def generate_recommendations(cls, category: RiskCategory, answers: Dict[str, str]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if category == RiskCategory.CONSERVATIVE:
            recommendations.extend([
                "Consider Fixed Deposits, Government Bonds, and Debt Mutual Funds",
                "Limit equity exposure to 20-30% of portfolio",
                "Focus on capital preservation over growth",
                "Avoid videos promoting high-risk assets"
            ])
            
            if answers.get("Q2") == "C":
                recommendations.append(
                    "⚠️ PRIORITY: Build emergency fund before investing"
                )
                
        elif category == RiskCategory.MODERATE:
            recommendations.extend([
                "Balanced portfolio: 50-60% equity, 40-50% debt",
                "Consider Index Funds and Blue-Chip stocks",
                "Systematic Investment Plans (SIP) recommended",
                "Be cautious with crypto (max 5-10% allocation)"
            ])
            
        else:  # AGGRESSIVE
            recommendations.extend([
                "Can handle high-volatility assets",
                "Suitable for growth stocks and crypto",
                "Long-term horizon allows for market cycles",
                "Focus on fundamental analysis over hype"
            ])
            
            if answers.get("Q4") == "A":
                recommendations.append(
                    "⚠️ High risk tolerance but low experience - educate yourself first"
                )
        
        return recommendations
    
    @classmethod
    def create_profile(cls, answers: Dict[str, str]) -> RiskProfile:
        """Create complete risk profile from answers"""
        from datetime import datetime
        
        # Validate answers
        if len(answers) != 9:
            raise ValueError(f"Expected 9 answers, got {len(answers)}")
        
        # Calculate score
        total_score = cls.calculate_score(answers)
        
        # Determine category
        category = cls.determine_category(total_score)
        
        # Generate constraints and recommendations
        constraints = cls.generate_constraints(category, answers)
        recommendations = cls.generate_recommendations(category, answers)
        
        return RiskProfile(
            total_score=total_score,
            category=category,
            answers=answers,
            constraints=constraints,
            recommendations=recommendations,
            completed_at=datetime.utcnow().isoformat()
        )
    
    @classmethod
    def get_personalized_warning(
        cls, 
        profile: RiskProfile, 
        asset_class: str, 
        hype_score: float
    ) -> Optional[str]:
        """
        Generate personalized warning based on user profile and asset being analyzed
        
        This is the core "AI thinking" - the system considers:
        1. User's risk tolerance
        2. Asset class volatility
        3. User's specific answers (e.g., panic threshold)
        4. Hype level of the content
        """
        warnings = []
        
        # Conservative users
        if profile.category == RiskCategory.CONSERVATIVE:
            
            # Check asset class alignment
            if asset_class in ["crypto", "cryptocurrency", "altcoin", "meme_coin"]:
                warnings.append(
                    f"🚨 CRITICAL MISMATCH: You selected 'Capital Protection' as your goal "
                    f"(Q3), but cryptocurrency can drop 50%+ in days. This conflicts with "
                    f"your {profile.answers.get('Q5', 'stated')} maximum tolerable drop."
                )
            
            if asset_class in ["microcap", "penny_stock", "options", "derivatives"]:
                warnings.append(
                    f"⚠️ HIGH RISK: You indicated stress during market crashes (Q7: "
                    f"'{RiskProfileCalculator.QUESTIONS['Q7']['options'].get(profile.answers.get('Q7', 'A'))}'), "
                    f"but {asset_class} assets are extremely volatile."
                )
            
            # Check hype level
            if hype_score > 40:
                warnings.append(
                    f"🚨 EMOTIONAL MANIPULATION DETECTED: This video uses high-pressure tactics. "
                    f"Given your conservative profile, this is a RED FLAG for predatory content."
                )
        
        # Moderate users
        elif profile.category == RiskCategory.MODERATE:
            
            if asset_class in ["meme_coin", "penny_stock"] and hype_score > 60:
                warnings.append(
                    f"⚠️ CAUTION: High-risk asset + extreme hype. You indicated 'Balanced Growth' "
                    f"(Q3), but this content promotes speculation over fundamentals."
                )
        
        # Aggressive users - minimal warnings, focus on scams
        else:
            if hype_score > 90:
                warnings.append(
                    f"⚠️ SCAM ALERT: Even with your high risk tolerance, this content shows "
                    f"signs of pump-and-dump manipulation. Verify claims independently."
                )
        
        return " | ".join(warnings) if warnings else None


# API Request/Response Models
class QuestionnaireRequest(BaseModel):
    """Request to submit questionnaire answers"""
    answers: Dict[str, str] = Field(
        ...,
        example={
            "Q1": "A",
            "Q2": "B",
            "Q3": "A",
            "Q4": "A",
            "Q5": "A",
            "Q6": "B",
            "Q7": "A",
            "Q8": "A",
            "Q9": "B"
        }
    )


class QuestionnaireResponse(BaseModel):
    """Response with calculated risk profile"""
    profile: RiskProfile
    message: str

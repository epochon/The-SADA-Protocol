"""
Internal Deliberation Engine for HypeSlayer

This module implements a multi-stage decision-making process with:
1. Understanding Phase - What do we know? What's missing?
2. Analysis Phase - Facts, risks, ethics, alternatives
3. Self-Check Phase - Confidence scoring and contradiction detection
4. Decision Gate - Act/Refuse/Escalate based on confidence and risk

The agent MUST refuse when:
- Confidence < 50%
- Risk > 70%
- Critical information is missing
- Contradictions are detected
"""

from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DecisionAction(str, Enum):
    """Possible decision outcomes"""
    ACT_CONFIDENTLY = "ACT_CONFIDENTLY"
    ACT_WITH_WARNING = "ACT_WITH_WARNING"
    REFUSE = "REFUSE"
    ASK_FOR_MORE = "ASK_FOR_MORE"
    ESCALATE = "ESCALATE"


class DeliberationPhase(str, Enum):
    """Stages of internal deliberation"""
    UNDERSTAND = "UNDERSTAND"
    ANALYZE = "ANALYZE"
    SELF_CHECK = "SELF_CHECK"
    DECISION_GATE = "DECISION_GATE"


class UnderstandingResult(BaseModel):
    """Results from the Understanding phase"""
    available_info: List[str]
    missing_info: List[str]
    data_quality: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)


class AnalysisResult(BaseModel):
    """Results from the Analysis phase"""
    facts: List[str]
    risks: List[str]
    ethical_concerns: List[str]
    alternatives: List[str]
    contradictions: List[str]
    risk_score: float = Field(ge=0, le=100)


class SelfCheckResult(BaseModel):
    """Results from the Self-Check phase"""
    evidence_quality: float = Field(ge=0, le=100)
    data_completeness: float = Field(ge=0, le=100)
    contradiction_count: int
    confidence_score: float = Field(ge=0, le=100)
    what_could_go_wrong: List[str]


class DecisionGateResult(BaseModel):
    """Final decision from the Decision Gate"""
    action: DecisionAction
    confidence: float
    risk: float
    reasoning: str
    warnings: List[str]
    refusal_reason: Optional[str] = None


class DeliberationLog(BaseModel):
    """Complete deliberation process log"""
    phase: DeliberationPhase
    timestamp: str
    details: Dict
    output: str


class InternalDeliberationEngine:
    """
    Multi-stage deliberation engine with epistemic refusal
    
    Decision Flow:
    1. UNDERSTAND: Assess what we know and what's missing
    2. ANALYZE: Examine facts, risks, ethics, alternatives
    3. SELF_CHECK: Score confidence and identify issues
    4. DECISION_GATE: Make final decision based on thresholds
    """
    
    # Decision thresholds
    CONFIDENCE_THRESHOLD_REFUSE = 50
    CONFIDENCE_THRESHOLD_WARNING = 80
    RISK_THRESHOLD_REFUSE = 70
    
    @classmethod
    def phase_1_understand(
        cls,
        transcript: Optional[str],
        entities: Optional[Dict],
        market_data: Optional[Dict]
    ) -> UnderstandingResult:
        """
        Phase 1: UNDERSTAND
        Question: What info do I have? What's missing?
        """
        available_info = []
        missing_info = []
        
        # Check transcript
        if transcript and len(transcript) > 50:
            available_info.append(f"Transcript ({len(transcript)} chars)")
        else:
            missing_info.append("Valid transcript")
        
        # Check entities
        if entities and entities.get("asset"):
            ticker = entities.get("asset", {}).get("ticker")
            if ticker:
                available_info.append(f"Ticker identified: {ticker}")
            else:
                missing_info.append("Clear ticker symbol")
        else:
            missing_info.append("Financial entities (ticker, claim)")
        
        # Check claim
        if entities and entities.get("claim"):
            available_info.append(f"Claim extracted: {entities['claim'][:50]}...")
        else:
            missing_info.append("Specific financial claim")
        
        # Check market data
        if market_data and market_data.get("current_price"):
            available_info.append("Real-time market data")
        else:
            missing_info.append("Market data for verification")
        
        # Calculate scores
        total_checks = len(available_info) + len(missing_info)
        data_quality = (len(available_info) / total_checks * 100) if total_checks > 0 else 0
        completeness_score = max(0, 100 - (len(missing_info) * 25))
        
        return UnderstandingResult(
            available_info=available_info,
            missing_info=missing_info,
            data_quality=data_quality,
            completeness_score=completeness_score
        )
    
    @classmethod
    def phase_2_analyze(
        cls,
        entities: Optional[Dict],
        verification: Optional[Dict],
        sentiment: Optional[Dict],
        understanding: UnderstandingResult
    ) -> AnalysisResult:
        """
        Phase 2: ANALYZE
        Question: What are the facts, risks, ethics, alternatives?
        """
        facts = []
        risks = []
        ethical_concerns = []
        alternatives = []
        contradictions = []
        
        # Extract facts
        if entities:
            if entities.get("asset"):
                facts.append(f"Asset: {entities['asset'].get('ticker', 'Unknown')}")
            if entities.get("claim"):
                facts.append(f"Claim: {entities['claim']}")
        
        if verification:
            if verification.get("real_data"):
                real_data = verification["real_data"]
                if real_data.get("current_price"):
                    facts.append(f"Current price: ${real_data['current_price']}")
                if real_data.get("recommendation"):
                    facts.append(f"Analyst rating: {real_data['recommendation']}")
        
        # Identify risks
        if understanding.completeness_score < 50:
            risks.append("Incomplete data - high uncertainty")
        
        if sentiment and sentiment.get("hype_penalty", 0) > 60:
            risks.append("Extreme hype detected - potential manipulation")
        
        if verification and verification.get("discrepancy_score", 0) > 50:
            risks.append("Claim contradicts market data")
        
        # Check for contradictions
        if verification:
            discrepancies = verification.get("discrepancy_details", [])
            if discrepancies:
                contradictions.extend(discrepancies)
        
        # Ethical concerns
        if entities and entities.get("asset", {}).get("asset_type") in ["meme_coin", "unknown"]:
            if sentiment and sentiment.get("hype_penalty", 0) > 70:
                ethical_concerns.append(
                    "High-risk asset + extreme hype = potential pump-and-dump scheme"
                )
        
        # Suggest alternatives
        if len(risks) > 0:
            alternatives.append("Request more specific information from user")
        if len(contradictions) > 0:
            alternatives.append("Refuse and explain contradictions")
        if understanding.completeness_score < 70:
            alternatives.append("Ask for clearer video or additional context")
        
        # Calculate risk score
        risk_score = 0
        risk_score += (100 - understanding.completeness_score) * 0.3
        risk_score += sentiment.get("hype_penalty", 0) * 0.4 if sentiment else 0
        risk_score += verification.get("discrepancy_score", 0) * 0.3 if verification else 0
        risk_score = min(risk_score, 100)
        
        return AnalysisResult(
            facts=facts,
            risks=risks,
            ethical_concerns=ethical_concerns,
            alternatives=alternatives,
            contradictions=contradictions,
            risk_score=risk_score
        )
    
    @classmethod
    def phase_3_self_check(
        cls,
        understanding: UnderstandingResult,
        analysis: AnalysisResult,
        verification: Optional[Dict]
    ) -> SelfCheckResult:
        """
        Phase 3: SELF-CHECK
        Question: How confident am I? What could go wrong?
        """
        # Evidence quality (from verification)
        evidence_quality = 0
        if verification:
            evidence_quality = verification.get("evidence_quality", 0) * 100
        
        # Data completeness (from understanding)
        data_completeness = understanding.completeness_score
        
        # Contradiction count
        contradiction_count = len(analysis.contradictions)
        
        # Calculate final confidence score (weighted average)
        confidence_score = (
            evidence_quality * 0.4 +
            data_completeness * 0.3 +
            (100 - analysis.risk_score) * 0.2 +
            (100 if contradiction_count == 0 else max(0, 100 - contradiction_count * 20)) * 0.1
        )
        
        # What could go wrong?
        what_could_go_wrong = []
        
        if evidence_quality < 50:
            what_could_go_wrong.append(
                "Low evidence quality - market data may be incomplete or unreliable"
            )
        
        if data_completeness < 70:
            what_could_go_wrong.append(
                "Missing critical information - could make wrong decision"
            )
        
        if contradiction_count > 0:
            what_could_go_wrong.append(
                f"Found {contradiction_count} contradiction(s) - claim may be false"
            )
        
        if analysis.risk_score > 60:
            what_could_go_wrong.append(
                "High risk score - user could lose money if they trust this content"
            )
        
        if len(analysis.ethical_concerns) > 0:
            what_could_go_wrong.append(
                "Ethical red flags detected - content may be predatory"
            )
        
        return SelfCheckResult(
            evidence_quality=evidence_quality,
            data_completeness=data_completeness,
            contradiction_count=contradiction_count,
            confidence_score=confidence_score,
            what_could_go_wrong=what_could_go_wrong
        )
    
    @classmethod
    def phase_4_decision_gate(
        cls,
        self_check: SelfCheckResult,
        analysis: AnalysisResult,
        understanding: UnderstandingResult
    ) -> DecisionGateResult:
        """
        Phase 4: DECISION GATE
        Question: Should I act, refuse, or ask for help?
        
        Decision Rules:
        - Confidence < 50% → REFUSE
        - Risk > 70% → REFUSE
        - Missing critical info → ASK_FOR_MORE
        - Confidence 50-80% → ACT_WITH_WARNING
        - Confidence > 80% + Low Risk → ACT_CONFIDENTLY
        """
        confidence = self_check.confidence_score
        risk = analysis.risk_score
        warnings = []
        refusal_reason = None
        
        # RULE 1: Confidence < 50% → REFUSE
        if confidence < cls.CONFIDENCE_THRESHOLD_REFUSE:
            return DecisionGateResult(
                action=DecisionAction.REFUSE,
                confidence=confidence,
                risk=risk,
                reasoning="Confidence too low to make a reliable decision",
                warnings=[],
                refusal_reason=(
                    f"I don't have enough information to answer safely. "
                    f"My confidence is only {confidence:.1f}%, which is below the "
                    f"minimum threshold of {cls.CONFIDENCE_THRESHOLD_REFUSE}%."
                )
            )
        
        # RULE 2: Risk > 70% → REFUSE
        if risk > cls.RISK_THRESHOLD_REFUSE:
            return DecisionGateResult(
                action=DecisionAction.REFUSE,
                confidence=confidence,
                risk=risk,
                reasoning="Risk too high - stakes are too high to decide alone",
                warnings=[],
                refusal_reason=(
                    f"The stakes are too high for me to decide alone. "
                    f"Risk score: {risk:.1f}%. "
                    f"Reasons: {', '.join(analysis.risks)}"
                )
            )
        
        # RULE 3: Contradictions detected → REFUSE
        if self_check.contradiction_count > 0:
            return DecisionGateResult(
                action=DecisionAction.REFUSE,
                confidence=confidence,
                risk=risk,
                reasoning="Contradictions found in the data",
                warnings=[],
                refusal_reason=(
                    f"I found {self_check.contradiction_count} contradiction(s) in the data:\n" +
                    "\n".join(f"• {c}" for c in analysis.contradictions)
                )
            )
        
        # RULE 4: Missing critical info → ASK_FOR_MORE
        if len(understanding.missing_info) >= 2:
            return DecisionGateResult(
                action=DecisionAction.ASK_FOR_MORE,
                confidence=confidence,
                risk=risk,
                reasoning="Critical information missing",
                warnings=[],
                refusal_reason=(
                    f"I need more information to analyze this safely. Missing:\n" +
                    "\n".join(f"• {info}" for info in understanding.missing_info)
                )
            )
        
        # RULE 5: Confidence 50-80% → ACT_WITH_WARNING
        if confidence < cls.CONFIDENCE_THRESHOLD_WARNING:
            warnings = [
                f"⚠️ Moderate confidence ({confidence:.1f}%) - treat this analysis with caution",
                *[f"⚠️ {concern}" for concern in analysis.ethical_concerns],
                *[f"⚠️ {risk}" for risk in analysis.risks]
            ]
            
            return DecisionGateResult(
                action=DecisionAction.ACT_WITH_WARNING,
                confidence=confidence,
                risk=risk,
                reasoning="Moderate confidence - proceeding with warnings",
                warnings=warnings,
                refusal_reason=None
            )
        
        # RULE 6: Confidence > 80% + Low Risk → ACT_CONFIDENTLY
        if confidence >= cls.CONFIDENCE_THRESHOLD_WARNING and risk < 30:
            return DecisionGateResult(
                action=DecisionAction.ACT_CONFIDENTLY,
                confidence=confidence,
                risk=risk,
                reasoning="High confidence and low risk - safe to proceed",
                warnings=[],
                refusal_reason=None
            )
        
        # Default: ACT_WITH_WARNING (high confidence but moderate risk)
        warnings = [
            f"⚠️ Risk level: {risk:.1f}%",
            *[f"⚠️ {concern}" for concern in analysis.ethical_concerns]
        ]
        
        return DecisionGateResult(
            action=DecisionAction.ACT_WITH_WARNING,
            confidence=confidence,
            risk=risk,
            reasoning="High confidence but moderate risk - proceeding with caution",
            warnings=warnings,
            refusal_reason=None
        )
    
    @classmethod
    def deliberate(
        cls,
        transcript: Optional[str],
        entities: Optional[Dict],
        verification: Optional[Dict],
        sentiment: Optional[Dict],
        market_data: Optional[Dict] = None
    ) -> Tuple[DecisionGateResult, List[DeliberationLog]]:
        """
        Execute complete deliberation process
        
        Returns:
            - Final decision
            - Complete deliberation log
        """
        from datetime import datetime
        
        deliberation_log = []
        
        # Phase 1: UNDERSTAND
        understanding = cls.phase_1_understand(transcript, entities, market_data or verification.get("real_data") if verification else None)
        deliberation_log.append(DeliberationLog(
            phase=DeliberationPhase.UNDERSTAND,
            timestamp=datetime.utcnow().isoformat(),
            details={
                "available_info": understanding.available_info,
                "missing_info": understanding.missing_info,
                "data_quality": understanding.data_quality,
                "completeness": understanding.completeness_score
            },
            output=f"Data Quality: {understanding.data_quality:.1f}%, Completeness: {understanding.completeness_score:.1f}%"
        ))
        
        # Phase 2: ANALYZE
        analysis = cls.phase_2_analyze(entities, verification, sentiment, understanding)
        deliberation_log.append(DeliberationLog(
            phase=DeliberationPhase.ANALYZE,
            timestamp=datetime.utcnow().isoformat(),
            details={
                "facts": analysis.facts,
                "risks": analysis.risks,
                "contradictions": analysis.contradictions,
                "risk_score": analysis.risk_score
            },
            output=f"Risk Score: {analysis.risk_score:.1f}%, Contradictions: {len(analysis.contradictions)}"
        ))
        
        # Phase 3: SELF-CHECK
        self_check = cls.phase_3_self_check(understanding, analysis, verification)
        deliberation_log.append(DeliberationLog(
            phase=DeliberationPhase.SELF_CHECK,
            timestamp=datetime.utcnow().isoformat(),
            details={
                "evidence_quality": self_check.evidence_quality,
                "data_completeness": self_check.data_completeness,
                "confidence_score": self_check.confidence_score,
                "what_could_go_wrong": self_check.what_could_go_wrong
            },
            output=f"Confidence: {self_check.confidence_score:.1f}%, Potential Issues: {len(self_check.what_could_go_wrong)}"
        ))
        
        # Phase 4: DECISION GATE
        decision = cls.phase_4_decision_gate(self_check, analysis, understanding)
        deliberation_log.append(DeliberationLog(
            phase=DeliberationPhase.DECISION_GATE,
            timestamp=datetime.utcnow().isoformat(),
            details={
                "action": decision.action.value,
                "confidence": decision.confidence,
                "risk": decision.risk,
                "reasoning": decision.reasoning
            },
            output=f"Decision: {decision.action.value}"
        ))
        
        return decision, deliberation_log


# Test scenarios for validation
class TestScenarios:
    """
    Test scenarios across difficulty levels
    """
    
    @staticmethod
    def easy_should_act():
        """Easy: Clear, low-risk decision"""
        return {
            "transcript": "Apple reported strong Q4 earnings with revenue of $90 billion",
            "entities": {
                "asset": {"ticker": "AAPL", "asset_type": "stock"},
                "claim": "Apple revenue is $90 billion"
            },
            "verification": {
                "evidence_quality": 0.95,
                "discrepancy_score": 5,
                "real_data": {"current_price": 150, "revenue": 90000000000}
            },
            "sentiment": {
                "hype_penalty": 10,
                "sentiment_score": 0.3
            }
        }
    
    @staticmethod
    def medium_act_with_warning():
        """Medium: Some uncertainty"""
        return {
            "transcript": "Tesla might reach $500 by end of year based on delivery numbers",
            "entities": {
                "asset": {"ticker": "TSLA", "asset_type": "stock"},
                "claim": "Tesla will reach $500"
            },
            "verification": {
                "evidence_quality": 0.65,
                "discrepancy_score": 30,
                "real_data": {"current_price": 250}
            },
            "sentiment": {
                "hype_penalty": 45,
                "sentiment_score": 0.6
            }
        }
    
    @staticmethod
    def hard_must_refuse():
        """Hard: High risk or low confidence"""
        return {
            "transcript": "This coin will 100x next week! Don't miss out!",
            "entities": {
                "asset": {"ticker": "SCAMCOIN", "asset_type": "meme_coin"},
                "claim": "Will 100x next week"
            },
            "verification": {
                "evidence_quality": 0.1,
                "discrepancy_score": 95,
                "real_data": None
            },
            "sentiment": {
                "hype_penalty": 95,
                "sentiment_score": 0.95
            }
        }
    
    @staticmethod
    def adversarial_always_refuse():
        """Adversarial: Manipulation attempts"""
        return {
            "transcript": "Trust me bro, this is guaranteed money",
            "entities": None,
            "verification": None,
            "sentiment": {
                "hype_penalty": 100,
                "sentiment_score": 0.99
            }
        }

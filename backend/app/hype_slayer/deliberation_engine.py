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
from datetime import datetime, timezone

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
    data_quality: float = Field(ge=0.0, le=100.0)
    completeness_score: float = Field(ge=0.0, le=100.0)


class AnalysisResult(BaseModel):
    """Results from the Analysis phase"""
    facts: List[str]
    risks: List[str]
    ethical_concerns: List[str]
    alternatives: List[str]
    contradictions: List[str]
    risk_score: float = Field(ge=0.0, le=100.0)


class SelfCheckResult(BaseModel):
    """Results from the Self-Check phase"""
    evidence_quality: float = Field(ge=0.0, le=100.0)
    data_completeness: float = Field(ge=0.0, le=100.0)
    contradiction_count: int = Field(ge=0)
    confidence_score: float = Field(ge=0.0, le=100.0)
    what_could_go_wrong: List[str]


class DecisionGateResult(BaseModel):
    """Final decision from the Decision Gate"""
    action: DecisionAction
    confidence: float = Field(ge=0.0, le=100.0)
    risk: float = Field(ge=0.0, le=100.0)
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
    """
    
    CONFIDENCE_THRESHOLD_REFUSE = 50.0
    CONFIDENCE_THRESHOLD_WARNING = 80.0
    RISK_THRESHOLD_REFUSE = 70.0
    
    @classmethod
    def phase_1_understand(
        cls,
        transcript: Optional[str],
        entities: Optional[Dict],
        market_data: Optional[Dict]
    ) -> UnderstandingResult:
        available_info = []
        missing_info = []
        
        # Security Fix: Handled whitespace-only transcripts (Line 249 original)
        if transcript and len(transcript.strip()) > 50:
            available_info.append(f"Transcript ({len(transcript)} chars)")
        else:
            missing_info.append("Valid transcript")
        
        if entities and entities.get("asset"):
            ticker = entities["asset"].get("ticker")
            if ticker:
                available_info.append(f"Ticker identified: {ticker}")
            else:
                missing_info.append("Clear ticker symbol")
        else:
            missing_info.append("Financial entities (ticker, claim)")
        
        if entities and entities.get("claim"):
            available_info.append(f"Claim extracted: {entities['claim'][:50]}...")
        else:
            missing_info.append("Specific financial claim")
        
        # Stability Fix: Added None check for market data fields
        if market_data and market_data.get("current_price") is not None:
            available_info.append("Real-time market data")
        else:
            missing_info.append("Market data for verification")
        
        total_checks = len(available_info) + len(missing_info)
        data_quality = (len(available_info) / total_checks * 100.0) if total_checks > 0 else 0.0
        completeness_score = max(0.0, 100.0 - (len(missing_info) * 25.0))
        
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
        facts = []
        risks = []
        ethical_concerns = []
        alternatives = []
        contradictions = []
        
        if entities:
            if entities.get("asset"):
                facts.append(f"Asset: {entities['asset'].get('ticker', 'Unknown')}")
            if entities.get("claim"):
                facts.append(f"Claim: {entities['claim']}")
        
        if verification:
            real_data = verification.get("real_data")
            if real_data:
                if real_data.get("current_price") is not None:
                    facts.append(f"Current price: ${real_data['current_price']}")
                if real_data.get("recommendation"):
                    facts.append(f"Analyst rating: {real_data['recommendation']}")
        
        if understanding.completeness_score < 50:
            risks.append("Incomplete data - high uncertainty")
        
        hype_penalty = sentiment.get("hype_penalty", 0) if sentiment else 0
        if hype_penalty > 60:
            risks.append("Extreme hype detected - potential manipulation")
        
        discrepancy_score = verification.get("discrepancy_score", 0) if verification else 0
        if discrepancy_score > 50:
            risks.append("Claim contradicts market data")
        
        if verification:
            discrepancies = verification.get("discrepancy_details", [])
            contradictions.extend(discrepancies)
        
        if entities and entities.get("asset", {}).get("asset_type") in ["meme_coin", "unknown"]:
            if hype_penalty > 70:
                ethical_concerns.append("Potential predatory scheme detected")
        
        if risks:
            alternatives.append("Request more specific information from user")
        if contradictions:
            alternatives.append("Refuse and explain contradictions")
        if understanding.completeness_score < 70:
            alternatives.append("Ask for additional context")
        
        # Stability Fix: Prevent negative risk score and ensured range validation
        risk_score = (100.0 - understanding.completeness_score) * 0.3
        risk_score += hype_penalty * 0.4
        risk_score += discrepancy_score * 0.3
        risk_score = min(max(risk_score, 0.0), 100.0)
        
        return AnalysisResult(
            facts=facts, risks=risks, ethical_concerns=ethical_concerns,
            alternatives=alternatives, contradictions=contradictions, risk_score=risk_score
        )
    
    @classmethod
    def phase_3_self_check(
        cls,
        understanding: UnderstandingResult,
        analysis: AnalysisResult,
        verification: Optional[Dict]
    ) -> SelfCheckResult:
        evidence_quality = (verification.get("evidence_quality", 0) * 100.0) if verification else 0.0
        data_completeness = understanding.completeness_score
        contradiction_count = len(analysis.contradictions)
        
        confidence_score = (
            evidence_quality * 0.4 +
            data_completeness * 0.3 +
            (100.0 - analysis.risk_score) * 0.2 +
            (100.0 if not contradiction_count else max(0.0, 100.0 - contradiction_count * 20.0)) * 0.1
        )
        
        what_could_go_wrong = []
        if evidence_quality < 50: what_could_go_wrong.append("Low evidence quality")
        if data_completeness < 70: what_could_go_wrong.append("Missing critical info")
        if contradiction_count > 0: what_could_go_wrong.append(f"Found {contradiction_count} contradiction(s)")
        if analysis.risk_score > 60: what_could_go_wrong.append("High risk content")
        if analysis.ethical_concerns: what_could_go_wrong.append("Ethical flags detected")
        
        return SelfCheckResult(
            evidence_quality=evidence_quality, data_completeness=data_completeness,
            contradiction_count=contradiction_count, confidence_score=confidence_score,
            what_could_go_wrong=what_could_go_wrong
        )
    
    @classmethod
    def phase_4_decision_gate(
        cls,
        self_check: SelfCheckResult,
        analysis: AnalysisResult,
        understanding: UnderstandingResult
    ) -> DecisionGateResult:
        confidence = self_check.confidence_score
        risk = analysis.risk_score
        
        if confidence < cls.CONFIDENCE_THRESHOLD_REFUSE:
            return DecisionGateResult(
                action=DecisionAction.REFUSE, confidence=confidence, risk=risk,
                reasoning="Confidence too low", warnings=[],
                refusal_reason=f"I don't have enough information to answer safely (Confidence: {confidence:.1f}%)."
            )
        
        if risk > cls.RISK_THRESHOLD_REFUSE:
            return DecisionGateResult(
                action=DecisionAction.REFUSE, confidence=confidence, risk=risk,
                reasoning="Risk level exceeded", warnings=[],
                refusal_reason=f"The stakes are too high for me to decide alone (Risk: {risk:.1f}%)."
            )
        
        if self_check.contradiction_count > 0:
            return DecisionGateResult(
                action=DecisionAction.REFUSE, confidence=confidence, risk=risk,
                reasoning="Data contradictions", warnings=[],
                refusal_reason=f"I found {self_check.contradiction_count} contradiction(s) in the data."
            )
        
        if len(understanding.missing_info) >= 2:
            return DecisionGateResult(
                action=DecisionAction.ASK_FOR_MORE, confidence=confidence, risk=risk,
                reasoning="Multiple info gaps", warnings=[],
                refusal_reason="I need more information to analyze this safely."
            )
        
        if confidence < cls.CONFIDENCE_THRESHOLD_WARNING:
            return DecisionGateResult(
                action=DecisionAction.ACT_WITH_WARNING, confidence=confidence, risk=risk,
                reasoning="Moderate confidence",
                warnings=[f"⚠️ Caution: {r}" for r in analysis.risks] + [f"⚠️ {e}" for e in analysis.ethical_concerns]
            )
        
        return DecisionGateResult(
            action=DecisionAction.ACT_CONFIDENTLY if risk < 30 else DecisionAction.ACT_WITH_WARNING,
            confidence=confidence, risk=risk, reasoning="Sufficient confidence",
            warnings=[f"⚠️ {e}" for e in analysis.ethical_concerns]
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
        logs = []
        # Logical Fix: Corrected market_data precedence in ternary operator
        m_data = market_data if market_data is not None else (verification.get("real_data") if verification else None)
        
        u = cls.phase_1_understand(transcript, entities, m_data)
        # Security Fix: Switched to timezone-aware UTC datetime for Python 3.12+ (Line 316 original)
        logs.append(DeliberationLog(
            phase=DeliberationPhase.UNDERSTAND, timestamp=datetime.now(timezone.utc).isoformat(),
            details=u.dict(), output=f"Quality: {u.data_quality:.1f}%, Complete: {u.completeness_score:.1f}%"
        ))
        
        a = cls.phase_2_analyze(entities, verification, sentiment, u)
        logs.append(DeliberationLog(
            phase=DeliberationPhase.ANALYZE, timestamp=datetime.now(timezone.utc).isoformat(),
            details=a.dict(), output=f"Risk: {a.risk_score:.1f}%, Contradictions: {len(a.contradictions)}"
        ))
        
        s = cls.phase_3_self_check(u, a, verification)
        logs.append(DeliberationLog(
            phase=DeliberationPhase.SELF_CHECK, timestamp=datetime.now(timezone.utc).isoformat(),
            details=s.dict(), output=f"Confidence: {s.confidence_score:.1f}%"
        ))
        
        d = cls.phase_4_decision_gate(s, a, u)
        logs.append(DeliberationLog(
            phase=DeliberationPhase.DECISION_GATE, timestamp=datetime.now(timezone.utc).isoformat(),
            details=d.dict(), output=f"Result: {d.action}"
        ))
        
        return d, logs

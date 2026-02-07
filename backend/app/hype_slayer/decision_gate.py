"""
Decision Gate Service
Calculates final confidence score and makes REFUSE/VERIFY decision
"""

from typing import Dict, Any, List
from datetime import datetime


# Decision threshold - below this = REFUSE
CONFIDENCE_THRESHOLD = 50


def calculate_confidence(
    evidence_quality: float,
    data_completeness: float,
    discrepancy_score: int,
    hype_penalty: int
) -> Dict[str, Any]:
    """
    Calculate final confidence score using the HypeSlayer formula.
    
    Formula: Score = ((Evidence_Quality + Data_Completeness) * 50) - (Discrepancy_Penalty + Hype_Penalty)
    
    Args:
        evidence_quality: 0.0 to 1.0 - quality of financial data
        data_completeness: 0.0 to 1.0 - how complete the data is
        discrepancy_score: 0-100 - discrepancy between claim and reality
        hype_penalty: 0-100 - penalty for hype/suspicious content
        
    Returns:
        dict: Decision with confidence score and reasoning
    """
    reasoning = []
    
    # Validate inputs
    evidence_quality = max(0.0, min(1.0, evidence_quality))
    data_completeness = max(0.0, min(1.0, data_completeness))
    discrepancy_score = max(0, min(100, discrepancy_score))
    hype_penalty = max(0, min(100, hype_penalty))
    
    # Calculate base score (0-100 from evidence and completeness)
    base_score = (evidence_quality + data_completeness) * 50
    reasoning.append(f"Base score from evidence quality ({evidence_quality:.2f}) and data completeness ({data_completeness:.2f}): {base_score:.1f}")
    
    # Apply penalties (scaled to 0-50 range each)
    discrepancy_penalty = discrepancy_score * 0.5
    hype_penalty_scaled = hype_penalty * 0.5
    
    if discrepancy_score > 0:
        reasoning.append(f"Discrepancy penalty: -{discrepancy_penalty:.1f} (raw score: {discrepancy_score})")
    if hype_penalty > 0:
        reasoning.append(f"Hype penalty: -{hype_penalty_scaled:.1f} (raw score: {hype_penalty})")
    
    # Final score
    final_score = base_score - discrepancy_penalty - hype_penalty_scaled
    final_score = max(0, min(100, final_score))  # Clamp to 0-100
    
    # Make decision
    decision = "VERIFY" if final_score >= CONFIDENCE_THRESHOLD else "REFUSE"
    
    # Add decision reasoning
    if decision == "REFUSE":
        if hype_penalty > 40:
            reasoning.append("⚠️ Content flagged as highly promotional/hyped")
        if discrepancy_score > 50:
            reasoning.append("⚠️ Significant discrepancies with verified market data")
        if evidence_quality < 0.5:
            reasoning.append("⚠️ Insufficient evidence quality to verify claims")
        reasoning.append(f"❌ DECISION: REFUSE (Score {final_score:.1f} below threshold {CONFIDENCE_THRESHOLD})")
    else:
        reasoning.append(f"✅ DECISION: VERIFY (Score {final_score:.1f} meets threshold {CONFIDENCE_THRESHOLD})")
    
    return {
        "confidence_score": round(final_score, 1),
        "decision": decision,
        "threshold": CONFIDENCE_THRESHOLD,
        "score_breakdown": {
            "base_score": round(base_score, 1),
            "discrepancy_penalty": round(discrepancy_penalty, 1),
            "hype_penalty": round(hype_penalty_scaled, 1)
        },
        "inputs": {
            "evidence_quality": evidence_quality,
            "data_completeness": data_completeness,
            "discrepancy_score": discrepancy_score,
            "hype_penalty": hype_penalty
        },
        "reasoning": reasoning,
        "timestamp": datetime.now().isoformat()
    }


def make_final_decision(
    transcript_result: Dict,
    entity_result: Dict,
    verification_result: Dict,
    sentiment_result: Dict
) -> Dict[str, Any]:
    """
    Orchestrate final decision from all analysis components.
    
    This is the main decision function that combines all service outputs.
    """
    # Check for critical failures first
    if transcript_result.get("status") == "error":
        return {
            "decision": "REFUSE",
            "confidence_score": 0,
            "reason": "Failed to fetch transcript",
            "error": transcript_result.get("error")
        }
    
    if entity_result.get("status") == "refused":
        return {
            "decision": "REFUSE",
            "confidence_score": 0,
            "reason": "Could not identify financial asset/claim",
            "refuse_reason": entity_result.get("refuse_reason")
        }
    
    # Extract scores from each service
    evidence_quality = verification_result.get("evidence_quality", 0.5)
    
    # Data completeness from entity extraction confidence
    data_completeness = entity_result.get("confidence", 0.5)
    
    # Discrepancy score from fact checker
    discrepancy_score = verification_result.get("discrepancy_score", 50)
    
    # Hype penalty from sentiment
    hype_penalty = sentiment_result.get("hype_penalty", 0)
    
    # Calculate final confidence
    decision_result = calculate_confidence(
        evidence_quality=evidence_quality,
        data_completeness=data_completeness,
        discrepancy_score=discrepancy_score,
        hype_penalty=hype_penalty
    )
    
    # Add context from other services
    decision_result["entity"] = entity_result.get("asset")
    decision_result["claim"] = entity_result.get("claim")
    decision_result["hype_level"] = sentiment_result.get("hype_level")
    decision_result["verification_status"] = verification_result.get("verification_status")
    
    return decision_result

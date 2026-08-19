from uuid import UUID
from datetime import datetime, timezone
from typing import Dict, Optional

from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentOut
from app.services.scoring_service import compute_weighted_score


def grade_from_score(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


class InMemoryAssessmentStore:
    """
    Standing in for the real `assessments` table (UNIQUE(session_id) — one
    row per session, aggregating across all attempts). Swap for real DB
    once Intern 5's tables are wired in.
    """

    def __init__(self):
        self._assessments: Dict[UUID, Assessment] = {}

    def record_attempt(
        self,
        session_id: UUID,
        predicted_sign: str,
        expected_sign: str,
        confidence: float,
        hold_seconds: Optional[float] = None,
        hand_shape_score: Optional[float] = None,
        finger_position_score: Optional[float] = None,
    ) -> Assessment:
        assessment = self._assessments.get(session_id)
        if assessment is None:
            assessment = Assessment(session_id=session_id)
            self._assessments[session_id] = assessment

        confidence = max(0.0, min(1.0, confidence))  # clamp defensively
        is_correct = predicted_sign == expected_sign

        result = compute_weighted_score(
            is_correct=is_correct,
            confidence=confidence,
            hold_seconds=hold_seconds,
            hand_shape_score=hand_shape_score,
            finger_position_score=finger_position_score,
        )
        attempt_score = result["score"]

        assessment.total_predictions += 1
        if is_correct:
            assessment.correct_predictions += 1
        assessment.score_sum += attempt_score
        assessment.last_breakdown = result  # for Day 3 Feedback Engine

        stats = assessment.sign_stats.setdefault(expected_sign, {"correct": 0, "total": 0})
        stats["total"] += 1
        if is_correct:
            stats["correct"] += 1

        return assessment

    def complete(self, session_id: UUID) -> Optional[Assessment]:
        assessment = self._assessments.get(session_id)
        if assessment is None:
            return None
        assessment.completed_at = datetime.now(timezone.utc)
        return assessment

    def get(self, session_id: UUID) -> Optional[Assessment]:
        return self._assessments.get(session_id)

    def to_out(self, assessment: Assessment) -> AssessmentOut:
        total = assessment.total_predictions
        accuracy_percentage = (assessment.correct_predictions / total * 100) if total else 0.0
        avg_score = (assessment.score_sum / total) if total else 0.0
        return AssessmentOut(
            session_id=assessment.session_id,
            correct_predictions=assessment.correct_predictions,
            total_predictions=total,
            accuracy_percentage=round(accuracy_percentage, 2),
            score=round(avg_score, 2),
            grade=grade_from_score(avg_score),
            completed_at=assessment.completed_at,
        )


assessment_store = InMemoryAssessmentStore()
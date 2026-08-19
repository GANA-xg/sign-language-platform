from uuid import UUID
from typing import List, Dict

from app.schemas.recommendation import RecommendationItem, RecommendationOut
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store

# Rule thresholds — per SRS Day 4:
# "below 70% in the last 3 attempts = recommend extra practice"
ACCURACY_THRESHOLD = 70.0
MIN_ATTEMPTS = 3


def get_recommendations(user_id: UUID) -> RecommendationOut:
    """
    Looks across all of a user's sessions, aggregates per-sign
    correct/total counts, and flags any sign where recent accuracy
    is below the threshold AND the sign has been attempted enough
    times to be statistically meaningful.
    """
    sessions = practice_store.get_sessions_by_user(user_id)

    # Aggregate per-sign stats across all sessions for this user
    # sign -> {"correct": int, "total": int}
    combined: Dict[str, Dict[str, int]] = {}

    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment is None:
            continue
        for sign, stats in assessment.sign_stats.items():
            entry = combined.setdefault(sign, {"correct": 0, "total": 0})
            entry["correct"] += stats["correct"]
            entry["total"] += stats["total"]

    recommendations: List[RecommendationItem] = []

    for sign, stats in combined.items():
        total = stats["total"]
        if total < MIN_ATTEMPTS:
            # Not enough attempts to make a reliable recommendation
            continue

        accuracy = (stats["correct"] / total) * 100

        if accuracy < ACCURACY_THRESHOLD:
            recommendations.append(RecommendationItem(
                sign=sign,
                reason=f"You've attempted sign '{sign}' {total} times with only {round(accuracy, 1)}% accuracy — some extra practice would help.",
                recent_accuracy=round(accuracy, 2),
                attempts_checked=total,
            ))

    # Sort by worst accuracy first so the most urgent signs appear at the top
    recommendations.sort(key=lambda r: r.recent_accuracy)

    return RecommendationOut(
        user_id=user_id,
        recommendations=recommendations,
        total_recommended=len(recommendations),
    )
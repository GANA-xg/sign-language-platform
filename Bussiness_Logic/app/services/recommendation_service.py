from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import List, Dict

from app.schemas.recommendation import RecommendationItem, RecommendationOut
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.schemas.practice import SessionStatus

# Rule thresholds
ACCURACY_THRESHOLD = 70.0
MIN_WEIGHTED_ATTEMPTS = 2.0     # minimum weighted attempts before flagging

# Recency weights
WEIGHT_LAST_7_DAYS = 1.0
WEIGHT_8_TO_30_DAYS = 0.5
WEIGHT_OLDER = 0.25


def _get_recency_weight(session_date: datetime) -> float:
    now = datetime.now(timezone.utc)
    # Make session_date timezone-aware if it isn't
    if session_date.tzinfo is None:
        session_date = session_date.replace(tzinfo=timezone.utc)
    days_ago = (now - session_date).days
    if days_ago <= 7:
        return WEIGHT_LAST_7_DAYS
    if days_ago <= 30:
        return WEIGHT_8_TO_30_DAYS
    return WEIGHT_OLDER


def get_recommendations(user_id: UUID) -> RecommendationOut:
    """
    Recency-weighted recommendation engine (M3 upgrade from M2).
    Recent attempts count more than old ones — a sign improved recently
    won't keep getting flagged just because of old bad attempts.
    """
    sessions = practice_store.get_sessions_by_user(user_id)

    # Per-sign weighted stats: sign -> {"weighted_correct": float, "weighted_total": float}
    weighted_stats: Dict[str, Dict[str, float]] = {}

    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment is None:
            continue

        weight = _get_recency_weight(session.started_at)

        for sign, stats in assessment.sign_stats.items():
            entry = weighted_stats.setdefault(sign, {"weighted_correct": 0.0, "weighted_total": 0.0})
            entry["weighted_correct"] += stats["correct"] * weight
            entry["weighted_total"] += stats["total"] * weight

    recommendations: List[RecommendationItem] = []

    for sign, stats in weighted_stats.items():
        weighted_total = stats["weighted_total"]
        if weighted_total < MIN_WEIGHTED_ATTEMPTS:
            continue

        weighted_accuracy = (stats["weighted_correct"] / weighted_total) * 100

        if weighted_accuracy < ACCURACY_THRESHOLD:
            recommendations.append(RecommendationItem(
                sign=sign,
                reason=f"Your recent practice shows {round(weighted_accuracy, 1)}% accuracy on sign '{sign}' — some extra practice would help.",
                recent_accuracy=round(weighted_accuracy, 2),
                attempts_checked=round(weighted_total, 1),
            ))

    recommendations.sort(key=lambda r: r.recent_accuracy)

    return RecommendationOut(
        user_id=user_id,
        recommendations=recommendations,
        total_recommended=len(recommendations),
    )
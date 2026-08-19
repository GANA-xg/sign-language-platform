from uuid import UUID
from typing import List, Dict
from collections import defaultdict

from app.schemas.analytics import AnalyticsOut, WeeklyStatOut, WeeklyAnalyticsOut
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.schemas.practice import SessionStatus

WEAK_SIGN_ACCURACY_THRESHOLD = 60.0
WEAK_SIGN_MIN_ATTEMPTS = 2


def compute_analytics(user_id: UUID) -> AnalyticsOut:
    sessions = practice_store.get_sessions_by_user(user_id)
    total_sessions = len(sessions)
    lessons_completed = len({
        s.lesson_id for s in sessions if s.status == SessionStatus.completed
    })

    accuracies: List[float] = []
    combined_sign_stats: Dict[str, Dict[str, int]] = {}

    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment is None or assessment.total_predictions == 0:
            continue
        accuracies.append(assessment.correct_predictions / assessment.total_predictions * 100)
        for sign, stats in assessment.sign_stats.items():
            combined = combined_sign_stats.setdefault(sign, {"correct": 0, "total": 0})
            combined["correct"] += stats["correct"]
            combined["total"] += stats["total"]

    average_accuracy = round(sum(accuracies) / len(accuracies), 2) if accuracies else 0.0
    weak_signs = [
        sign for sign, stats in combined_sign_stats.items()
        if stats["total"] >= WEAK_SIGN_MIN_ATTEMPTS
        and (stats["correct"] / stats["total"] * 100) < WEAK_SIGN_ACCURACY_THRESHOLD
    ]

    return AnalyticsOut(
        user_id=user_id,
        total_sessions=total_sessions,
        lessons_completed=lessons_completed,
        average_accuracy=average_accuracy,
        weak_signs=weak_signs,
    )


def compute_weekly_analytics(user_id: UUID) -> WeeklyAnalyticsOut:
    sessions = practice_store.get_sessions_by_user(user_id)

    week_buckets: Dict[str, list] = defaultdict(list)
    for session in sessions:
        week_label = session.started_at.strftime("%G-W%V")
        week_buckets[week_label].append(session)

    weekly_stats: List[WeeklyStatOut] = []

    for week_label in sorted(week_buckets.keys()):
        week_sessions = week_buckets[week_label]
        accuracies: List[float] = []
        sign_stats: Dict[str, Dict[str, int]] = {}

        for session in week_sessions:
            assessment = assessment_store.get(session.session_id)
            if assessment is None or assessment.total_predictions == 0:
                continue
            accuracies.append(
                assessment.correct_predictions / assessment.total_predictions * 100
            )
            for sign, stats in assessment.sign_stats.items():
                entry = sign_stats.setdefault(sign, {"correct": 0, "total": 0})
                entry["correct"] += stats["correct"]
                entry["total"] += stats["total"]

        avg_accuracy = round(sum(accuracies) / len(accuracies), 2) if accuracies else 0.0
        weak_signs = [
            sign for sign, stats in sign_stats.items()
            if stats["total"] >= WEAK_SIGN_MIN_ATTEMPTS
            and (stats["correct"] / stats["total"] * 100) < WEAK_SIGN_ACCURACY_THRESHOLD
        ]

        weekly_stats.append(WeeklyStatOut(
            week_label=week_label,
            sessions_count=len(week_sessions),
            average_accuracy=avg_accuracy,
            weak_signs=weak_signs,
        ))

    improvement_rate = None
    current_week_accuracy = None
    previous_week_accuracy = None

    if len(weekly_stats) >= 2:
        current = weekly_stats[-1].average_accuracy
        previous = weekly_stats[-2].average_accuracy
        current_week_accuracy = current
        previous_week_accuracy = previous
        if previous > 0:
            improvement_rate = round(((current - previous) / previous) * 100, 2)
    elif len(weekly_stats) == 1:
        current_week_accuracy = weekly_stats[0].average_accuracy

    return WeeklyAnalyticsOut(
        user_id=user_id,
        weeks=weekly_stats,
        improvement_rate=improvement_rate,
        current_week_accuracy=current_week_accuracy,
        previous_week_accuracy=previous_week_accuracy,
    )
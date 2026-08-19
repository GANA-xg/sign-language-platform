"""
Trainer Analytics Service

The backend API owns trainer -> learner assignments.

Backend role name:
    trainer

Backend endpoints:
    GET  /trainer/{trainer_id}/learners
    GET  /trainer/{trainer_id}/learners/details

This service only calculates analytics for the learners returned
by the backend.
"""

import httpx

from uuid import UUID
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from app.schemas.trainer_analytics import (
    LearnerAnalyticsOut,
    TrainerDashboardOut,
)

from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.services.analytics_service import compute_weekly_analytics
from app.services.certification_service import certification_store

from app.core.config import (
    BACKEND_API_URL,
    AI_SERVICE_TIMEOUT_SECONDS,
)


# ─────────────────────────────────────────────
# Engagement thresholds
# ─────────────────────────────────────────────

HIGH_ENGAGEMENT_SESSIONS_PER_WEEK = 4
LOW_ENGAGEMENT_SESSIONS_PER_WEEK = 2


# ─────────────────────────────────────────────
# Get learners assigned to trainer
# ─────────────────────────────────────────────

def get_learners_for_trainer(
    trainer_id: UUID,
    authorization: Optional[str] = None,
) -> List[UUID]:
    """
    Fetch learners assigned to a trainer from the backend API.

    Backend endpoint:

        GET /trainer/{trainer_id}/learners

    IMPORTANT:
    Backend DB role is "trainer".
    There is no "accessibility_trainer" role.
    """

    url = (
        f"{BACKEND_API_URL}"
        f"/trainer/{trainer_id}/learners"
    )

    headers = {}

    if authorization:
        headers["Authorization"] = authorization

    try:
        response = httpx.get(
            url,
            headers=headers,
            timeout=AI_SERVICE_TIMEOUT_SECONDS,
        )

        response.raise_for_status()

        raw = response.json()

        return [
            UUID(str(item))
            for item in raw
        ]

    except httpx.HTTPStatusError as exc:
        print(
            "Trainer learner API failed:",
            exc.response.status_code,
            exc.response.text,
        )
        return []

    except Exception as exc:
        print(
            "Trainer learner API error:",
            str(exc),
        )
        return []


def remove_learner_from_trainer(
    trainer_id: UUID,
    learner_id: UUID,
    authorization: Optional[str] = None,
) -> bool:
    """
    Remove a learner from a trainer's assignments.

    Calls the Backend API:

        DELETE /trainer/{trainer_id}/learners/{learner_id}
    """

    url = (
        f"{BACKEND_API_URL}"
        f"/trainer/{trainer_id}/learners/{learner_id}"
    )

    headers = {}

    if authorization:
        headers["Authorization"] = authorization

    try:
        response = httpx.delete(
            url,
            headers=headers,
            timeout=AI_SERVICE_TIMEOUT_SECONDS,
        )

        return response.status_code in (200, 204)

    except Exception:
        return False


# ─────────────────────────────────────────────
# Sessions
# ─────────────────────────────────────────────

def _sessions_this_week(
    user_id: UUID,
) -> int:

    sessions = (
        practice_store
        .get_sessions_by_user(user_id)
    )

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(days=7)
    )

    return sum(
        1
        for session in sessions
        if session.started_at >= cutoff
    )


# ─────────────────────────────────────────────
# Engagement
# ─────────────────────────────────────────────

def _engagement_level(
    sessions_this_week: int,
) -> str:

    if (
        sessions_this_week
        >= HIGH_ENGAGEMENT_SESSIONS_PER_WEEK
    ):
        return "High"

    if (
        sessions_this_week
        >= LOW_ENGAGEMENT_SESSIONS_PER_WEEK
    ):
        return "Medium"

    return "Low"


# ─────────────────────────────────────────────
# Assessment score
# ─────────────────────────────────────────────

def _avg_assessment_score(
    user_id: UUID,
) -> float:

    sessions = (
        practice_store
        .get_sessions_by_user(user_id)
    )

    scores = []

    for session in sessions:

        assessment = (
            assessment_store
            .get(session.session_id)
        )

        if (
            assessment is None
            or assessment.total_predictions == 0
        ):
            continue

        score = (
            assessment.score_sum
            / assessment.total_predictions
        )

        scores.append(score)

    if not scores:
        return 0.0

    return round(
        sum(scores) / len(scores),
        2,
    )


# ─────────────────────────────────────────────
# Skill development
# ─────────────────────────────────────────────

def _skill_development_trend(
    user_id: UUID,
) -> Optional[float]:

    weekly = compute_weekly_analytics(
        user_id
    )

    return weekly.improvement_rate


# ─────────────────────────────────────────────
# Certification
# ─────────────────────────────────────────────

def _certification_status(
    user_id: UUID,
) -> Dict[str, Optional[str]]:

    exams = (
        certification_store
        .get_exams_by_user(user_id)
    )

    completed = [
        exam
        for exam in exams
        if exam.status == "completed"
    ]

    passed = [
        exam
        for exam in completed
        if exam.passed
    ]

    if passed:

        highest = max(
            passed,
            key=lambda exam:
                len(exam.required_signs),
        )

        return {
            "status": "Certified",
            "highest_certified_level":
                highest.level,
        }

    if completed:

        return {
            "status": "In Progress",
            "highest_certified_level": None,
        }

    return {
        "status": "Not Started",
        "highest_certified_level": None,
    }


# ─────────────────────────────────────────────
# Per learner analytics
# ─────────────────────────────────────────────

def compute_learner_analytics(
    learner_id: UUID,
) -> LearnerAnalyticsOut:

    sessions_this_week = (
        _sessions_this_week(
            learner_id
        )
    )

    certification = (
        _certification_status(
            learner_id
        )
    )

    return LearnerAnalyticsOut(
        learner_id=learner_id,

        sessions_this_week=
            sessions_this_week,

        engagement_level=
            _engagement_level(
                sessions_this_week
            ),

        avg_assessment_score=
            _avg_assessment_score(
                learner_id
            ),

        skill_development_trend=
            _skill_development_trend(
                learner_id
            ),

        certification_status=
            certification["status"],

        highest_certified_level=
            certification[
                "highest_certified_level"
            ],
    )


# ─────────────────────────────────────────────
# Trainer dashboard
# ─────────────────────────────────────────────

def compute_trainer_dashboard(
    trainer_id: UUID,
    authorization: Optional[str] = None,
) -> TrainerDashboardOut:

    learner_ids = (
        get_learners_for_trainer(
            trainer_id,
            authorization,
        )
    )

    learners = [
        compute_learner_analytics(
            learner_id
        )
        for learner_id in learner_ids
    ]

    count = len(learners)

    avg_sessions = (
        round(
            sum(
                learner.sessions_this_week
                for learner in learners
            ) / count,
            1,
        )
        if count
        else 0.0
    )

    avg_score = (
        round(
            sum(
                learner.avg_assessment_score
                for learner in learners
            ) / count,
            2,
        )
        if count
        else 0.0
    )

    certified_count = sum(
        1
        for learner in learners
        if learner.certification_status
        == "Certified"
    )

    low_engagement_count = sum(
        1
        for learner in learners
        if learner.engagement_level
        == "Low"
    )

    return TrainerDashboardOut(
        trainer_id=trainer_id,

        assigned_learners_count=count,

        avg_sessions_per_week=
            avg_sessions,

        avg_assessment_score=
            avg_score,

        certified_count=
            certified_count,

        low_engagement_count=
            low_engagement_count,

        learners=learners,
    )
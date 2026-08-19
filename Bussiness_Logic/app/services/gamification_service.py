from uuid import UUID
from datetime import datetime, timezone, date, timedelta
from typing import List, Dict

from app.schemas.gamification import BadgeOut, StreakOut, GamificationOut
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.schemas.practice import SessionStatus


# ── Badge definitions ─────────────────────────────────────────────────
# Each badge has an id, name, description, and a check function.
# Add more badges here as M3 progresses (leaderboard, export, etc.)

def _check_first_step(user_id: UUID, sessions, combined_sign_stats, average_accuracy) -> bool:
    """Earned: completed at least 1 session."""
    return any(s.status == SessionStatus.completed for s in sessions)


def _check_on_a_roll(user_id: UUID, sessions, combined_sign_stats, average_accuracy) -> bool:
    """Earned: current streak of 3+ days."""
    streak = _compute_streak(sessions)
    return streak["current_streak"] >= 3


def _check_alphabet_master(user_id: UUID, sessions, combined_sign_stats, average_accuracy) -> bool:
    """Earned: practiced 10+ distinct signs with average accuracy >= 80%."""
    if len(combined_sign_stats) < 10:
        return False
    return average_accuracy >= 80.0


def _check_perfect_session(user_id: UUID, sessions, combined_sign_stats, average_accuracy) -> bool:
    """Earned: at least one session with 100% accuracy."""
    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment and assessment.total_predictions > 0:
            acc = assessment.correct_predictions / assessment.total_predictions * 100
            if acc == 100.0:
                return True
    return False


def _check_consistent_learner(user_id: UUID, sessions, combined_sign_stats, average_accuracy) -> bool:
    """Earned: completed 5+ sessions."""
    completed = [s for s in sessions if s.status == SessionStatus.completed]
    return len(completed) >= 5


BADGE_DEFINITIONS = [
    {
        "badge_id": "first_step",
        "name": "First Step",
        "description": "Complete your first practice session.",
        "check": _check_first_step,
    },
    {
        "badge_id": "on_a_roll",
        "name": "On a Roll 🔥",
        "description": "Practice 3 days in a row.",
        "check": _check_on_a_roll,
    },
    {
        "badge_id": "alphabet_master",
        "name": "Alphabet Master",
        "description": "Practice 10+ distinct signs with average accuracy ≥ 80%.",
        "check": _check_alphabet_master,
    },
    {
        "badge_id": "perfect_session",
        "name": "Perfect Session ⭐",
        "description": "Get 100% accuracy in a single session.",
        "check": _check_perfect_session,
    },
    {
        "badge_id": "consistent_learner",
        "name": "Consistent Learner",
        "description": "Complete 5 or more practice sessions.",
        "check": _check_consistent_learner,
    },
]


def _compute_streak(sessions) -> dict:
    """
    Computes current and longest streak from session dates.
    A streak is a consecutive sequence of calendar days with at least one session.
    """
    if not sessions:
        return {"current_streak": 0, "longest_streak": 0, "last_practiced_date": None}

    # Get unique practice dates, sorted descending
    practice_dates = sorted(
        set(s.started_at.date() for s in sessions),
        reverse=True
    )

    today = datetime.now(timezone.utc).date()
    last_date = practice_dates[0]

    # If last practice was more than 1 day ago, current streak is 0
    if (today - last_date).days > 1:
        current_streak = 0
    else:
        # Count backwards from most recent date
        current_streak = 1
        for i in range(1, len(practice_dates)):
            if (practice_dates[i - 1] - practice_dates[i]).days == 1:
                current_streak += 1
            else:
                break

    # Compute longest streak
    longest_streak = 1
    temp = 1
    for i in range(1, len(practice_dates)):
        if (practice_dates[i - 1] - practice_dates[i]).days == 1:
            temp += 1
            longest_streak = max(longest_streak, temp)
        else:
            temp = 1

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_practiced_date": str(last_date),
    }


def compute_gamification(user_id: UUID) -> GamificationOut:
    sessions = practice_store.get_sessions_by_user(user_id)

    # Aggregate cross-session stats (same pattern as analytics/certificate)
    accuracies = []
    combined_sign_stats: Dict[str, Dict[str, int]] = {}

    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment is None or assessment.total_predictions == 0:
            continue
        accuracies.append(
            assessment.correct_predictions / assessment.total_predictions * 100
        )
        for sign, stats in assessment.sign_stats.items():
            entry = combined_sign_stats.setdefault(sign, {"correct": 0, "total": 0})
            entry["correct"] += stats["correct"]
            entry["total"] += stats["total"]

    average_accuracy = (sum(accuracies) / len(accuracies)) if accuracies else 0.0

    # Compute streak
    streak_data = _compute_streak(sessions)
    streak = StreakOut(
        current_streak=streak_data["current_streak"],
        longest_streak=streak_data["longest_streak"],
        last_practiced_date=streak_data["last_practiced_date"],
    )

    # Evaluate badges
    badges: List[BadgeOut] = []
    for defn in BADGE_DEFINITIONS:
        earned = defn["check"](user_id, sessions, combined_sign_stats, average_accuracy)
        badges.append(BadgeOut(
            badge_id=defn["badge_id"],
            name=defn["name"],
            description=defn["description"],
            earned=earned,
            earned_at=datetime.now(timezone.utc) if earned else None,
        ))

    earned_count = sum(1 for b in badges if b.earned)

    return GamificationOut(
        user_id=user_id,
        streak=streak,
        badges=badges,
        total_badges_earned=earned_count,
    )
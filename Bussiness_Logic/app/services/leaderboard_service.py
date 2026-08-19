from uuid import UUID
from typing import List, Dict

from app.schemas.leaderboard import LeaderboardEntry, LeaderboardOut, RankBy
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.services.gamification_service import _compute_streak
from app.schemas.practice import SessionStatus


def compute_leaderboard(rank_by: RankBy = RankBy.accuracy) -> LeaderboardOut:
    """
    Ranks all learners who have at least one session.
    Pulls data from in-memory stores — no DB dependency yet.
    """

    # Step 1: collect all unique user_ids from practice_store
    all_sessions = list(practice_store._sessions.values())
    user_ids = list(set(s.user_id for s in all_sessions))

    entries: List[LeaderboardEntry] = []

    for user_id in user_ids:
        user_sessions = [s for s in all_sessions if s.user_id == user_id]
        completed = [s for s in user_sessions if s.status == SessionStatus.completed]

        # Compute average accuracy
        accuracies = []
        for session in user_sessions:
            assessment = assessment_store.get(session.session_id)
            if assessment and assessment.total_predictions > 0:
                accuracies.append(
                    assessment.correct_predictions / assessment.total_predictions * 100
                )
        average_accuracy = round(sum(accuracies) / len(accuracies), 2) if accuracies else 0.0

        # Compute streak
        streak_data = _compute_streak(user_sessions)
        current_streak = streak_data["current_streak"]

        score = average_accuracy if rank_by == RankBy.accuracy else float(current_streak)

        entries.append(LeaderboardEntry(
            rank=0,             # assigned below after sorting
            user_id=user_id,
            average_accuracy=average_accuracy,
            current_streak=current_streak,
            total_sessions=len(completed),
            score=score,
        ))

    # Step 2: sort by score descending, assign ranks
    entries.sort(key=lambda e: e.score, reverse=True)
    for i, entry in enumerate(entries):
        entry.rank = i + 1

    return LeaderboardOut(
        rank_by=rank_by,
        entries=entries,
        total_learners=len(entries),
    )
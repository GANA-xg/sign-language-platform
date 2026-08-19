from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from enum import Enum


class RankBy(str, Enum):
    accuracy = "accuracy"
    streak = "streak"


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    average_accuracy: float
    current_streak: int
    total_sessions: int
    score: float                    # the field being ranked on (accuracy or streak)


class LeaderboardOut(BaseModel):
    rank_by: RankBy
    entries: List[LeaderboardEntry]
    total_learners: int
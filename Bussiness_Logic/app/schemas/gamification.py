from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class BadgeOut(BaseModel):
    badge_id: str
    name: str
    description: str
    earned: bool
    earned_at: Optional[datetime] = None


class StreakOut(BaseModel):
    current_streak: int         # consecutive days practiced
    longest_streak: int         # all-time best streak
    last_practiced_date: Optional[str] = None  # e.g. "2026-07-20"


class GamificationOut(BaseModel):
    user_id: UUID
    streak: StreakOut
    badges: List[BadgeOut]
    total_badges_earned: int
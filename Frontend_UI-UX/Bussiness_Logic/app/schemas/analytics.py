from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class AnalyticsOut(BaseModel):
    user_id: UUID
    total_sessions: int
    lessons_completed: int
    average_accuracy: float
    weak_signs: List[str]


class WeeklyStatOut(BaseModel):
    week_label: str
    sessions_count: int
    average_accuracy: float
    weak_signs: List[str]


class WeeklyAnalyticsOut(BaseModel):
    user_id: UUID
    weeks: List[WeeklyStatOut]
    improvement_rate: Optional[float] = None
    current_week_accuracy: Optional[float] = None
    previous_week_accuracy: Optional[float] = None
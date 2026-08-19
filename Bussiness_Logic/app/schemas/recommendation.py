from pydantic import BaseModel
from uuid import UUID
from typing import List


class RecommendationItem(BaseModel):
    sign: str
    reason: str
    recent_accuracy: float      # accuracy % across the last N attempts
    attempts_checked: float       # how many recent attempts were looked at


class RecommendationOut(BaseModel):
    user_id: UUID
    recommendations: List[RecommendationItem]
    total_recommended: int
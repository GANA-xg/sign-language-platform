from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class AssessmentAttemptRequest(BaseModel):
    session_id: UUID
    expected_sign: str      # string for now, matches AI contract; will become sign_id later
    predicted_sign: str     # from Intern 3's AI service
    confidence: float       # 0.0–1.0, from Intern 3's AI service


class AssessmentOut(BaseModel):
    session_id: UUID
    correct_predictions: int
    total_predictions: int
    accuracy_percentage: float   # correct/total * 100
    score: float                 # weighted score, see Tier 1 formula
    grade: str                   # simple letter bucket
    completed_at: Optional[datetime] = None
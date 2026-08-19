from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class ProgressReportOut(BaseModel):
    user_id: UUID
    generated_at: datetime

    # Session stats
    total_sessions: int
    completed_sessions: int
    total_practice_time_seconds: int

    # Accuracy
    average_accuracy: float
    grade: str

    # Signs
    distinct_signs_practiced: int
    weak_signs: List[str]
    strong_signs: List[str]   # signs with accuracy >= 80%

    # Weekly summary
    current_week_accuracy: Optional[float] = None
    improvement_rate: Optional[float] = None

    # Recommendations
    recommended_for_practice: List[str]

    # Certificate
    certificate_eligible: bool
    certificate_reasons_failed: List[str]

class ProgressReportPDFRequest(BaseModel):
    learner_name: str
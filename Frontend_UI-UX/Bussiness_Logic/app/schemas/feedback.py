from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import List, Optional


class FeedbackType(str, Enum):
    improvement = "improvement"
    correction = "correction"
    praise = "praise"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class FeedbackItem(BaseModel):
    feedback_type: FeedbackType
    message: str
    severity: Severity


class FeedbackGenerateRequest(BaseModel):
    session_id: UUID
    expected_sign: Optional[str] = None


class FeedbackOut(BaseModel):
    session_id: UUID
    feedback: List[FeedbackItem]
    generated_at: datetime


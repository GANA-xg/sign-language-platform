from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime


class EligibilityOut(BaseModel):
    user_id: UUID
    eligible: bool
    reasons_failed: List[str]   # empty if eligible
    criteria_met: List[str]     # which rules passed
    checked_at: datetime


class CertificateOut(BaseModel):
    user_id: UUID
    learner_name: str
    issued_at: datetime
    average_accuracy: float
    total_sessions: int
    signs_practiced: int
    certificate_id: str         # unique ID for the certificate

class CertificateGenerateRequest(BaseModel):
    learner_name: str
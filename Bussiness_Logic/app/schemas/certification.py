"""
Certification Exam — Pydantic Schemas

A Certification Exam is distinct from regular Practice (app/schemas/practice.py):
it's a fixed-length, multi-sign test scored with the same weighted formula
used since M2 (scoring_service.py), graded pass/fail against a per-level
threshold. 4 levels per the M4 SRS (Section 9 / FR-4): Beginner,
Intermediate, Advanced, Professional.
"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional, List


class CertificationLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    professional = "professional"


class CertificationExamStartRequest(BaseModel):
    user_id: UUID
    level: CertificationLevel


class CertificationExamOut(BaseModel):
    exam_id: UUID
    user_id: UUID
    level: CertificationLevel
    required_signs: List[str]
    status: str
    started_at: datetime


class CertificationAttemptRequest(BaseModel):
    exam_id: UUID
    expected_sign: str
    predicted_sign: str             # from Intern 3's AI service
    confidence: float                # 0.0–1.0
    hold_seconds: Optional[float] = None


class CertificationAttemptResultOut(BaseModel):
    exam_id: UUID
    expected_sign: str
    predicted_sign: str
    is_correct: bool
    attempt_score: float
    signs_completed: int
    signs_remaining: int
    exam_status: str


class CertificationResultOut(BaseModel):
    exam_id: UUID
    user_id: UUID
    level: CertificationLevel
    score: float
    accuracy_percentage: float
    correct_predictions: int
    total_predictions: int
    pass_threshold: float
    passed: bool
    completed_at: datetime
    certificate_id: Optional[str] = None


class CertificationLevelInfo(BaseModel):
    level: CertificationLevel
    num_signs: int
    pass_threshold: float
    description: str


class CertificationCertificateRequest(BaseModel):
    learner_name: str
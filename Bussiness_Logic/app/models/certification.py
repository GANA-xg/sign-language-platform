"""
Certification Exam — Data Model (STUB)

Plain Python dataclass standing in for the real `certification_exams` table
until Intern 5's DB integration lands. Mirrors the same "swap for real ORM
later" pattern used by app/models/practice.py and app/models/assessment.py.

TODO (Intern 5 DB integration): Replace with a real SQLAlchemy model and
swap InMemoryCertificationExamStore (services/certification_service.py)
for actual DB calls — field names are kept 1:1 so the swap is drop-in.
"""

from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class CertificationExam:
    exam_id: UUID
    user_id: UUID
    level: str                      # "beginner" | "intermediate" | "advanced" | "professional"
    required_signs: List[str]       # fixed set of signs this exam attempt covers
    status: str = "in_progress"     # "in_progress" | "completed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # One entry per attempted sign: {"expected_sign", "predicted_sign", "is_correct", "attempt_score"}
    attempt_results: List[Dict[str, Any]] = field(default_factory=list)

    # Set on completion
    score: Optional[float] = None          # average weighted score across all required signs
    correct_predictions: int = 0
    total_predictions: int = 0
    passed: Optional[bool] = None
    pass_threshold: Optional[float] = None
    certificate_id: Optional[str] = None   # set once a certificate is issued for this exam
"""
Certification Exam Service (Milestone 4, Day 2)

Implements the formal Certification Exam workflow required by the M4 SRS
(Section 9 / FR-4): a structured, multi-sign exam — distinct from regular
Practice — scored with the SAME weighted formula used since M2
(scoring_service.compute_weighted_score), graded pass/fail against a
per-level threshold, across 4 levels: Beginner, Intermediate, Advanced,
Professional.

Design notes:
- Reuses scoring_service.compute_weighted_score() rather than inventing a
  second scoring formula, per the SRS instruction to score exams "using
  your existing weighted-scoring formula".
- Signs are drawn from the full A-Z alphabet already validated by
  Intern 3's model (no new datasets — SRS ground rule).
- In-memory store, same pattern as practice_service/assessment_service,
  designed as a drop-in replacement for a real DB table later.
"""

import random
import string
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.models.certification import CertificationExam
from app.schemas.certification import (
    CertificationLevel,
    CertificationExamOut,
    CertificationAttemptResultOut,
    CertificationResultOut,
    CertificationLevelInfo,
)
from app.services.scoring_service import compute_weighted_score

# ── Level configuration ──────────────────────────────────────────────
# Adjust these constants to tune difficulty without touching logic,
# same pattern as certificate_service.py's eligibility constants.
FULL_ALPHABET = list(string.ascii_uppercase)  # 26 signs, matches Intern 3's model

LEVEL_CONFIG: Dict[CertificationLevel, dict] = {
    CertificationLevel.beginner: {
        "num_signs": 8,
        "pass_threshold": 60.0,
        "description": "Covers a core subset of the alphabet. Entry-level certification.",
    },
    CertificationLevel.intermediate: {
        "num_signs": 14,
        "pass_threshold": 70.0,
        "description": "Covers just over half the alphabet at a higher accuracy bar.",
    },
    CertificationLevel.advanced: {
        "num_signs": 20,
        "pass_threshold": 80.0,
        "description": "Covers most of the alphabet with a strict accuracy bar.",
    },
    CertificationLevel.professional: {
        "num_signs": 26,
        "pass_threshold": 85.0,
        "description": "Covers the full A-Z alphabet at the highest accuracy bar.",
    },
}


def get_level_info() -> List[CertificationLevelInfo]:
    return [
        CertificationLevelInfo(
            level=level,
            num_signs=cfg["num_signs"],
            pass_threshold=cfg["pass_threshold"],
            description=cfg["description"],
        )
        for level, cfg in LEVEL_CONFIG.items()
    ]


class InMemoryCertificationExamStore:
    """
    Standing in for real `certification_exams` table until Intern 5's DB
    integration lands. Swap for real ORM models later (see model docstring).
    """

    def __init__(self):
        self._exams: Dict[UUID, CertificationExam] = {}

    def start_exam(self, user_id: UUID, level: CertificationLevel) -> CertificationExam:
        cfg = LEVEL_CONFIG[level]
        required_signs = random.sample(FULL_ALPHABET, cfg["num_signs"])

        exam = CertificationExam(
            exam_id=uuid4(),
            user_id=user_id,
            level=level.value,
            required_signs=required_signs,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            pass_threshold=cfg["pass_threshold"],
        )
        self._exams[exam.exam_id] = exam
        return exam

    def record_attempt(
        self,
        exam_id: UUID,
        expected_sign: str,
        predicted_sign: str,
        confidence: float,
        hold_seconds: Optional[float] = None,
    ) -> CertificationExam:
        exam = self._exams.get(exam_id)
        if exam is None:
            raise ValueError("Certification exam not found")
        if exam.status != "in_progress":
            raise ValueError(f"Exam already {exam.status}, cannot record more attempts")

        already_attempted = {a["expected_sign"] for a in exam.attempt_results}
        if expected_sign not in exam.required_signs:
            raise ValueError(f"'{expected_sign}' is not part of this exam's required signs")
        if expected_sign in already_attempted:
            raise ValueError(f"'{expected_sign}' has already been attempted in this exam")

        confidence = max(0.0, min(1.0, confidence))
        is_correct = predicted_sign == expected_sign

        result = compute_weighted_score(
            is_correct=is_correct,
            confidence=confidence,
            hold_seconds=hold_seconds,
        )
        attempt_score = result["score"]

        exam.attempt_results.append({
            "expected_sign": expected_sign,
            "predicted_sign": predicted_sign,
            "is_correct": is_correct,
            "attempt_score": attempt_score,
        })
        exam.total_predictions += 1
        if is_correct:
            exam.correct_predictions += 1

        return exam

    def complete_exam(self, exam_id: UUID) -> CertificationExam:
        exam = self._exams.get(exam_id)
        if exam is None:
            raise ValueError("Certification exam not found")
        if exam.status == "completed":
            return exam  # idempotent — already completed

        if len(exam.attempt_results) < len(exam.required_signs):
            missing = len(exam.required_signs) - len(exam.attempt_results)
            raise ValueError(f"Exam cannot be completed — {missing} sign(s) not yet attempted")

        avg_score = sum(a["attempt_score"] for a in exam.attempt_results) / len(exam.attempt_results)
        exam.score = round(avg_score, 2)
        exam.passed = exam.score >= exam.pass_threshold
        exam.status = "completed"
        exam.completed_at = datetime.now(timezone.utc)
        return exam

    def get(self, exam_id: UUID) -> Optional[CertificationExam]:
        return self._exams.get(exam_id)

    def get_exams_by_user(self, user_id: UUID) -> List[CertificationExam]:
        return [e for e in self._exams.values() if e.user_id == user_id]

    def set_certificate_id(self, exam_id: UUID, certificate_id: str) -> None:
        exam = self._exams.get(exam_id)
        if exam is not None:
            exam.certificate_id = certificate_id

    # ── Output mappers ──────────────────────────────────────────────

    def to_out(self, exam: CertificationExam) -> CertificationExamOut:
        return CertificationExamOut(
            exam_id=exam.exam_id,
            user_id=exam.user_id,
            level=CertificationLevel(exam.level),
            required_signs=exam.required_signs,
            status=exam.status,
            started_at=exam.started_at,
        )

    def to_attempt_out(self, exam: CertificationExam, last_result: dict) -> CertificationAttemptResultOut:
        return CertificationAttemptResultOut(
            exam_id=exam.exam_id,
            expected_sign=last_result["expected_sign"],
            predicted_sign=last_result["predicted_sign"],
            is_correct=last_result["is_correct"],
            attempt_score=last_result["attempt_score"],
            signs_completed=len(exam.attempt_results),
            signs_remaining=len(exam.required_signs) - len(exam.attempt_results),
            exam_status=exam.status,
        )

    def to_result_out(self, exam: CertificationExam) -> CertificationResultOut:
        accuracy = (exam.correct_predictions / exam.total_predictions * 100) if exam.total_predictions else 0.0
        return CertificationResultOut(
            exam_id=exam.exam_id,
            user_id=exam.user_id,
            level=CertificationLevel(exam.level),
            score=exam.score,
            accuracy_percentage=round(accuracy, 2),
            correct_predictions=exam.correct_predictions,
            total_predictions=exam.total_predictions,
            pass_threshold=exam.pass_threshold,
            passed=exam.passed,
            completed_at=exam.completed_at,
            certificate_id=exam.certificate_id,
        )


certification_store = InMemoryCertificationExamStore()
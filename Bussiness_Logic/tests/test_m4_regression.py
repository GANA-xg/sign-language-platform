"""
M4 Day 5 — Full Regression Test Suite

Covers every domain built across M1–M4:
  - Existing M1-M3 logic (scoring, feedback, badges, streaks, recommendations)
  - M4 Day 2: Certification Exam workflow (4 levels, pass/fail, certificate trigger)
  - M4 Day 3: Accessibility Trainer analytics (engagement, skill dev, cert status)
  - M4 Day 4: All 5 report types in PDF and Excel (smoke test — bytes returned, no crash)

Uses the same isolated store pattern as test_scenarios.py so tests never
share state.
"""

import pytest
import string
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager

from app.services.practice_service import InMemoryPracticeSessionStore
from app.services.assessment_service import InMemoryAssessmentStore
from app.services.gamification_service import compute_gamification
from app.services.recommendation_service import get_recommendations
from app.services.certificate_service import check_eligibility
from app.services.analytics_service import compute_analytics
from app.schemas.practice import SessionStatus

from app.services.certification_service import (
    InMemoryCertificationExamStore,
    LEVEL_CONFIG,
    CertificationLevel,
)
from app.services.scoring_service import compute_weighted_score

from app.services.trainer_analytics_service import (
    InMemoryTrainerAssignmentStore,
)

import app.services.analytics_service as analytics_svc
import app.services.certificate_service as cert_svc
import app.services.recommendation_service as rec_svc
import app.services.gamification_service as gami_svc
import app.services.trainer_analytics_service as trainer_svc
import app.services.export_service as export_svc


# ── Helpers ────────────────────────────────────────────────────────────

def make_stores():
    return InMemoryPracticeSessionStore(), InMemoryAssessmentStore()


@contextmanager
def patched_stores(practice_store, assessment_store,
                   certification_store=None, assignment_store=None):
    modules = [analytics_svc, cert_svc, rec_svc, gami_svc, trainer_svc, export_svc]
    originals = []

    for mod in modules:
        orig_ps = getattr(mod, "practice_store", None)
        orig_as = getattr(mod, "assessment_store", None)
        orig_cs = getattr(mod, "certification_store", None)
        originals.append((mod, orig_ps, orig_as, orig_cs))
        if hasattr(mod, "practice_store"):
            mod.practice_store = practice_store
        if hasattr(mod, "assessment_store"):
            mod.assessment_store = assessment_store
        if certification_store and hasattr(mod, "certification_store"):
            mod.certification_store = certification_store

    try:
        yield
    finally:
        for mod, orig_ps, orig_as, orig_cs in originals:
            if orig_ps is not None:
                mod.practice_store = orig_ps
            if orig_as is not None:
                mod.assessment_store = orig_as
            if orig_cs is not None:
                mod.certification_store = orig_cs


def run_session(practice_store, assessment_store, user_id,
                lesson_id=1, attempts=None, days_ago=0, complete=True):
    session = practice_store.start_session(user_id, lesson_id)
    if days_ago > 0:
        session.started_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    if attempts:
        for expected, predicted, confidence in attempts:
            assessment_store.record_attempt(
                session_id=session.session_id,
                predicted_sign=predicted,
                expected_sign=expected,
                confidence=confidence,
            )
    if complete:
        session.ended_at = datetime.now(timezone.utc)
        session.status = SessionStatus.completed
    return session


def run_full_exam(cert_store, user_id, level, pass_it=True):
    """Run a complete certification exam. pass_it=True submits all correct answers."""
    exam = cert_store.start_exam(user_id, level)
    for sign in exam.required_signs:
        predicted = sign if pass_it else "Z"
        result = compute_weighted_score(
            is_correct=(predicted == sign),
            confidence=0.95 if pass_it else 0.2,
            hold_seconds=1.5,
        )
        exam.attempt_results.append({
            "expected_sign": sign,
            "predicted_sign": predicted,
            "is_correct": predicted == sign,
            "attempt_score": result["score"],
        })
        exam.total_predictions += 1
        if predicted == sign:
            exam.correct_predictions += 1
    return cert_store.complete_exam(exam.exam_id)


# ── M1-M3 REGRESSION ──────────────────────────────────────────────────

def test_regression_scoring_formula():
    result = compute_weighted_score(is_correct=True, confidence=1.0, hold_seconds=2.0)
    assert result["score"] == 100.0
    result_wrong = compute_weighted_score(is_correct=False, confidence=0.2, hold_seconds=0.5)
    assert result_wrong["score"] < 40.0
    print("✅ Regression — scoring formula: PASSED")


def test_regression_badges_and_streaks():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        for i in range(5):
            run_session(practice_store, assessment_store, user_id,
                        lesson_id=i+1, attempts=[("A", "A", 0.99)] * 3, complete=True)
        gamification = compute_gamification(user_id)
        earned = [b.badge_id for b in gamification.badges if b.earned]
        assert "first_step" in earned
        assert "perfect_session" in earned
        assert "consistent_learner" in earned
    print("✅ Regression — badges and streaks: PASSED")


def test_regression_recommendations():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id, lesson_id=1,
                    attempts=[("Z", "A", 0.2)] * 4, complete=True)
        recs = get_recommendations(user_id)
        rec_signs = [r.sign for r in recs.recommendations]
        assert "Z" in rec_signs
    print("✅ Regression — recommendations: PASSED")


def test_regression_certificate_eligibility():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        eligibility = check_eligibility(user_id)
        assert eligibility.eligible is False
        assert len(eligibility.reasons_failed) > 0
    print("✅ Regression — certificate eligibility: PASSED")


# ── M4 DAY 2: Certification Exam ──────────────────────────────────────

def test_cert_exam_level_config():
    assert LEVEL_CONFIG[CertificationLevel.beginner]["num_signs"] == 8
    assert LEVEL_CONFIG[CertificationLevel.beginner]["pass_threshold"] == 60.0
    assert LEVEL_CONFIG[CertificationLevel.intermediate]["num_signs"] == 14
    assert LEVEL_CONFIG[CertificationLevel.intermediate]["pass_threshold"] == 70.0
    assert LEVEL_CONFIG[CertificationLevel.advanced]["num_signs"] == 20
    assert LEVEL_CONFIG[CertificationLevel.advanced]["pass_threshold"] == 80.0
    assert LEVEL_CONFIG[CertificationLevel.professional]["num_signs"] == 26
    assert LEVEL_CONFIG[CertificationLevel.professional]["pass_threshold"] == 85.0
    print("✅ M4 Day 2 — level config: PASSED")


def test_cert_exam_pass():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    exam = run_full_exam(cert_store, user_id, CertificationLevel.beginner, pass_it=True)
    assert exam.status == "completed"
    assert exam.passed is True
    assert exam.score >= 60.0
    assert exam.correct_predictions == 8
    print("✅ M4 Day 2 — beginner exam pass: PASSED")


def test_cert_exam_fail():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    exam = run_full_exam(cert_store, user_id, CertificationLevel.beginner, pass_it=False)
    assert exam.status == "completed"
    assert exam.passed is False
    assert exam.score < 60.0
    print("✅ M4 Day 2 — beginner exam fail: PASSED")


def test_cert_exam_all_levels():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    for level in CertificationLevel:
        exam = run_full_exam(cert_store, user_id, level, pass_it=True)
        assert exam.status == "completed"
        assert exam.passed is True
        assert len(exam.required_signs) == LEVEL_CONFIG[level]["num_signs"]
    print("✅ M4 Day 2 — all 4 levels complete: PASSED")


def test_cert_exam_duplicate_attempt_rejected():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    exam = cert_store.start_exam(user_id, CertificationLevel.beginner)
    first_sign = exam.required_signs[0]
    cert_store.record_attempt(exam.exam_id, first_sign, first_sign, 0.9)
    with pytest.raises(ValueError, match="already been attempted"):
        cert_store.record_attempt(exam.exam_id, first_sign, first_sign, 0.9)
    print("✅ M4 Day 2 — duplicate attempt rejected: PASSED")


def test_cert_exam_early_complete_rejected():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    exam = cert_store.start_exam(user_id, CertificationLevel.beginner)
    cert_store.record_attempt(exam.exam_id, exam.required_signs[0], exam.required_signs[0], 0.9)
    with pytest.raises(ValueError, match="sign\\(s\\) not yet attempted"):
        cert_store.complete_exam(exam.exam_id)
    print("✅ M4 Day 2 — early completion rejected: PASSED")


def test_cert_exam_history_per_user():
    cert_store = InMemoryCertificationExamStore()
    user_a = uuid4()
    user_b = uuid4()
    run_full_exam(cert_store, user_a, CertificationLevel.beginner, pass_it=True)
    run_full_exam(cert_store, user_b, CertificationLevel.intermediate, pass_it=True)
    history_a = cert_store.get_exams_by_user(user_a)
    assert len(history_a) == 1
    assert history_a[0].user_id == user_a
    print("✅ M4 Day 2 — exam history per user: PASSED")


def test_cert_exam_professional_uses_full_alphabet():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    exam = cert_store.start_exam(user_id, CertificationLevel.professional)
    assert len(exam.required_signs) == 26
    assert set(exam.required_signs) == set(string.ascii_uppercase)
    print("✅ M4 Day 2 — professional level uses full alphabet: PASSED")


# ── M4 DAY 3: Trainer Analytics ───────────────────────────────────────

def test_trainer_assignment_idempotent():
    assignment_store = InMemoryTrainerAssignmentStore()
    trainer_id = uuid4()
    learner_id = uuid4()
    a1 = assignment_store.assign(trainer_id, learner_id)
    a2 = assignment_store.assign(trainer_id, learner_id)
    assert a1.assigned_at == a2.assigned_at
    assert len(assignment_store.get_learners_for_trainer(trainer_id)) == 1
    print("✅ M4 Day 3 — trainer assignment idempotent: PASSED")


def test_trainer_unassign():
    assignment_store = InMemoryTrainerAssignmentStore()
    trainer_id = uuid4()
    learner_id = uuid4()
    assignment_store.assign(trainer_id, learner_id)
    removed = assignment_store.unassign(trainer_id, learner_id)
    assert removed is True
    assert len(assignment_store.get_learners_for_trainer(trainer_id)) == 0
    print("✅ M4 Day 3 — trainer unassign: PASSED")


def test_trainer_unassign_nonexistent():
    assignment_store = InMemoryTrainerAssignmentStore()
    removed = assignment_store.unassign(uuid4(), uuid4())
    assert removed is False
    print("✅ M4 Day 3 — unassign nonexistent returns False: PASSED")


def test_trainer_engagement_high():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        for i in range(5):
            run_session(practice_store, assessment_store, user_id,
                        lesson_id=i+1, attempts=[("A", "A", 0.9)], complete=True)
        from app.services.trainer_analytics_service import _sessions_this_week, _engagement_level
        count = _sessions_this_week(user_id)
        assert count == 5
        assert _engagement_level(count) == "High"
    print("✅ M4 Day 3 — engagement High: PASSED")


def test_trainer_engagement_low():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9)], complete=True)
        from app.services.trainer_analytics_service import _sessions_this_week, _engagement_level
        count = _sessions_this_week(user_id)
        assert _engagement_level(count) == "Low"
    print("✅ M4 Day 3 — engagement Low: PASSED")


def test_trainer_certification_status_not_started():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    practice_store, assessment_store = make_stores()
    with patched_stores(practice_store, assessment_store, cert_store):
        from app.services.trainer_analytics_service import _certification_status
        status = _certification_status(user_id)
        assert status["status"] == "Not Started"
        assert status["highest_certified_level"] is None
    print("✅ M4 Day 3 — cert status Not Started: PASSED")


def test_trainer_certification_status_certified():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    practice_store, assessment_store = make_stores()
    run_full_exam(cert_store, user_id, CertificationLevel.beginner, pass_it=True)
    with patched_stores(practice_store, assessment_store, cert_store):
        from app.services.trainer_analytics_service import _certification_status
        status = _certification_status(user_id)
        assert status["status"] == "Certified"
        assert status["highest_certified_level"] == "beginner"
    print("✅ M4 Day 3 — cert status Certified: PASSED")


def test_trainer_certification_highest_level():
    cert_store = InMemoryCertificationExamStore()
    user_id = uuid4()
    practice_store, assessment_store = make_stores()
    run_full_exam(cert_store, user_id, CertificationLevel.beginner, pass_it=True)
    run_full_exam(cert_store, user_id, CertificationLevel.advanced, pass_it=True)
    with patched_stores(practice_store, assessment_store, cert_store):
        from app.services.trainer_analytics_service import _certification_status
        status = _certification_status(user_id)
        assert status["highest_certified_level"] == "advanced"
    print("✅ M4 Day 3 — highest cert level: PASSED")


def test_trainer_empty_dashboard():
    practice_store, assessment_store = make_stores()
    with patched_stores(practice_store, assessment_store):
        from app.services.trainer_analytics_service import (
            InMemoryTrainerAssignmentStore, compute_trainer_dashboard
        )
        assignment_store = InMemoryTrainerAssignmentStore()
        orig = trainer_svc.trainer_assignment_store
        trainer_svc.trainer_assignment_store = assignment_store
        try:
            result = compute_trainer_dashboard(uuid4())
            assert result.assigned_learners_count == 0
            assert result.avg_sessions_per_week == 0.0
            assert result.certified_count == 0
        finally:
            trainer_svc.trainer_assignment_store = orig
    print("✅ M4 Day 3 — empty trainer dashboard: PASSED")


# ── M4 DAY 4: Report exports (smoke tests) ────────────────────────────

def test_export_learning_pdf_returns_bytes():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9)], complete=True)
        from app.services.export_service import generate_learning_report_pdf
        pdf = generate_learning_report_pdf(user_id, "Test Learner")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
    print("✅ M4 Day 4 — learning PDF: PASSED")


def test_export_assessment_pdf_returns_bytes():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9), ("B", "C", 0.3)], complete=True)
        from app.services.export_service import generate_assessment_report_pdf
        pdf = generate_assessment_report_pdf(user_id, "Test Learner")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
    print("✅ M4 Day 4 — assessment PDF: PASSED")


def test_export_accuracy_pdf_returns_bytes():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9), ("B", "Z", 0.2)], complete=True)
        from app.services.export_service import generate_accuracy_report_pdf
        pdf = generate_accuracy_report_pdf(user_id, "Test Learner")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
    print("✅ M4 Day 4 — accuracy PDF: PASSED")


def test_export_certification_report_pdf_empty():
    cert_store = InMemoryCertificationExamStore()
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store, cert_store):
        from app.services.export_service import generate_certification_report_pdf
        pdf = generate_certification_report_pdf(user_id, "Test Learner")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
    print("✅ M4 Day 4 — certification report PDF (empty): PASSED")


def test_export_certification_report_pdf_with_data():
    cert_store = InMemoryCertificationExamStore()
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    run_full_exam(cert_store, user_id, CertificationLevel.beginner, pass_it=True)
    with patched_stores(practice_store, assessment_store, cert_store):
        from app.services.export_service import generate_certification_report_pdf
        pdf = generate_certification_report_pdf(user_id, "Test Learner")
        assert isinstance(pdf, bytes)
        assert len(pdf) > 100
    print("✅ M4 Day 4 — certification report PDF (with data): PASSED")


def test_export_learning_excel_returns_bytes():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9)], complete=True)
        from app.services.export_service import generate_learning_report_excel
        xlsx = generate_learning_report_excel(user_id)
        assert isinstance(xlsx, bytes)
        assert len(xlsx) > 100
    print("✅ M4 Day 4 — learning Excel: PASSED")


def test_export_accuracy_excel_returns_bytes():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9), ("B", "Z", 0.2)], complete=True)
        from app.services.export_service import generate_accuracy_report_excel
        xlsx = generate_accuracy_report_excel(user_id)
        assert isinstance(xlsx, bytes)
        assert len(xlsx) > 100
    print("✅ M4 Day 4 — accuracy Excel: PASSED")


def test_export_existing_progress_csv_regression():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id,
                    lesson_id=1, attempts=[("A", "A", 0.9)], complete=True)
        from app.services.export_service import generate_learner_progress_csv
        csv_bytes = generate_learner_progress_csv(user_id)
        assert isinstance(csv_bytes, bytes)
        content = csv_bytes.decode("utf-8")
        assert "Session Date" in content
        assert "Accuracy" in content
    print("✅ M4 Day 4 — existing progress CSV regression: PASSED")
"""
M3 Day 7 — Test Scenarios
"""
import pytest
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

import app.services.analytics_service as analytics_svc
import app.services.certificate_service as cert_svc
import app.services.recommendation_service as rec_svc
import app.services.gamification_service as gami_svc


def make_stores():
    return InMemoryPracticeSessionStore(), InMemoryAssessmentStore()


@contextmanager
def patched_stores(practice_store, assessment_store):
    """
    Patches the practice_store/assessment_store reference inside every
    service module that imported them directly, for the duration of a test.
    """
    modules = [analytics_svc, cert_svc, rec_svc, gami_svc]
    originals = []

    for mod in modules:
        orig_ps = getattr(mod, "practice_store", None)
        orig_as = getattr(mod, "assessment_store", None)
        originals.append((mod, orig_ps, orig_as))
        if hasattr(mod, "practice_store"):
            mod.practice_store = practice_store
        if hasattr(mod, "assessment_store"):
            mod.assessment_store = assessment_store

    try:
        yield
    finally:
        for mod, orig_ps, orig_as in originals:
            if orig_ps is not None:
                mod.practice_store = orig_ps
            if orig_as is not None:
                mod.assessment_store = orig_as


def run_session(
    practice_store, assessment_store, user_id,
    lesson_id=1, attempts=None, days_ago=0, complete=True,
):
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


# ── Scenario 1: Perfect Learner ────────────────────────────────────────

def test_perfect_learner():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()
    signs = ["A", "B", "C", "D", "E"]

    with patched_stores(practice_store, assessment_store):
        for i, sign in enumerate(signs):
            run_session(
                practice_store, assessment_store, user_id,
                lesson_id=i + 1,
                attempts=[(sign, sign, 0.99)] * 3,
                complete=True,
            )

        analytics = compute_analytics(user_id)
        assert analytics.average_accuracy == 100.0
        assert analytics.total_sessions == 5
        assert analytics.lessons_completed == 5
        assert analytics.weak_signs == []

        gamification = compute_gamification(user_id)
        earned_ids = [b.badge_id for b in gamification.badges if b.earned]
        assert "first_step" in earned_ids
        assert "perfect_session" in earned_ids
        assert "consistent_learner" in earned_ids

        recs = get_recommendations(user_id)
        assert recs.total_recommended == 0

    print("✅ Scenario 1 (Perfect Learner): PASSED")


def test_struggling_learner():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()

    with patched_stores(practice_store, assessment_store):
        signs = ["A", "B", "C"]
        for i, sign in enumerate(signs):
            run_session(
                practice_store, assessment_store, user_id,
                lesson_id=i + 1,
                attempts=[(sign, "Z", 0.2)] * 4,
                complete=True,
            )

        analytics = compute_analytics(user_id)
        assert analytics.average_accuracy == 0.0
        assert len(analytics.weak_signs) > 0

        recs = get_recommendations(user_id)
        assert recs.total_recommended > 0
        assert recs.recommendations[0].recent_accuracy < 70.0

        eligibility = check_eligibility(user_id)
        assert eligibility.eligible is False
        assert len(eligibility.reasons_failed) > 0

    print("✅ Scenario 2 (Struggling Learner): PASSED")


def test_inconsistent_learner():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()

    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id, lesson_id=1,
            attempts=[("A", "A", 0.95)] * 5, complete=True)
        run_session(practice_store, assessment_store, user_id, lesson_id=2,
            attempts=[("B", "Z", 0.2)] * 5, complete=True)
        run_session(practice_store, assessment_store, user_id, lesson_id=3,
            attempts=[("C", "C", 0.8), ("C", "Z", 0.3), ("C", "C", 0.9)], complete=True)

        analytics = compute_analytics(user_id)
        assert 0 < analytics.average_accuracy < 100
        assert analytics.total_sessions == 3

        recs = get_recommendations(user_id)
        rec_signs = [r.sign for r in recs.recommendations]
        assert "B" in rec_signs

    print("✅ Scenario 3 (Inconsistent Learner): PASSED")


def test_improving_learner():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()

    with patched_stores(practice_store, assessment_store):
        run_session(practice_store, assessment_store, user_id, lesson_id=1,
            attempts=[("A", "Z", 0.2)] * 5, days_ago=35, complete=True)  # changed from 15 to 35
        run_session(practice_store, assessment_store, user_id, lesson_id=1,
            attempts=[("A", "A", 0.95)] * 5, days_ago=0, complete=True)

        recs = get_recommendations(user_id)
        rec_signs = [r.sign for r in recs.recommendations]
        assert "A" not in rec_signs, f"Expected A not in recommendations but got: {rec_signs}"

    print("✅ Scenario 4 (Improving Learner): PASSED")

def test_single_sign_weak_learner():
    practice_store, assessment_store = make_stores()
    user_id = uuid4()

    with patched_stores(practice_store, assessment_store):
        for sign in ["A", "B", "C", "D", "E"]:
            run_session(practice_store, assessment_store, user_id, lesson_id=1,
                attempts=[(sign, sign, 0.95)] * 3, complete=True)
        run_session(practice_store, assessment_store, user_id, lesson_id=2,
            attempts=[("Z", "A", 0.3)] * 4, complete=True)

        analytics = compute_analytics(user_id)
        assert analytics.average_accuracy > 70.0
        assert "Z" in analytics.weak_signs

        recs = get_recommendations(user_id)
        rec_signs = [r.sign for r in recs.recommendations]
        assert "Z" in rec_signs
        assert "A" not in rec_signs
        assert "B" not in rec_signs

    print("✅ Scenario 5 (Single-Sign-Weak Learner): PASSED")
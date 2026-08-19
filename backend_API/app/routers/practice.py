from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.session import get_db
from app.models.user import User
from app.models.practice_session import PracticeSession
from app.models.practice_attempt import PracticeAttempt
from app.models.assessment_attempt import AssessmentAttempt
from app.schemas.practice import (
    PracticeSessionStart,
    PracticeSessionStartResponse,
    PracticeAttemptSubmit,
    PracticeAttemptSubmitResponse,
    AssessmentSubmit,
    AssessmentSubmitResponse,
)


router = APIRouter(prefix="/practice", tags=["Practice"])


@router.post(
    "/start",
    response_model=PracticeSessionStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a practice session",
)
def start_practice_session(
    payload: PracticeSessionStart,
    db: Session = Depends(get_db),
):
    """
    Start a new practice session for a user and lesson.

    - **user_id**: UUID of the user starting practice
    - **lesson_id**: ID of the lesson to practice
    """
    # Verify user exists
    user = db.query(User).filter(User.user_id == UUID(payload.user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verify lesson exists
    from app.models.lesson import Lesson
    lesson = db.query(Lesson).filter(Lesson.lesson_id == payload.lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    # Check if there's already an active session for this user-lesson combination
    existing = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.user_id == UUID(payload.user_id),
            PracticeSession.lesson_id == payload.lesson_id,
            PracticeSession.status == "active",
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active practice session already exists for this user and lesson",
        )

    session = PracticeSession(
        user_id=UUID(payload.user_id),
        lesson_id=payload.lesson_id,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return PracticeSessionStartResponse(
        session_id=str(session.session_id),
        message="Practice session started successfully",
    )


@router.post(
    "/{session_id}/attempt",
    response_model=PracticeAttemptSubmitResponse,
    summary="Submit a practice attempt",
)
def submit_practice_attempt(
    session_id: str,
    payload: PracticeAttemptSubmit,
    db: Session = Depends(get_db),
):
    """
    Submit a practice attempt for a session.

    - **session_id**: UUID of the practice session
    - **expected_sign**: The expected sign language gesture
    - **image_blob**: Base64-encoded image data
    - **attempt_started_at**: Timestamp when the attempt started
    """
    # Verify session exists and is active
    session = (
        db.query(PracticeSession)
        .filter(PracticeSession.session_id == UUID(session_id))
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found",
        )
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Practice session is not active",
        )

    attempt = PracticeAttempt(
        session_id=UUID(session_id),
        expected_sign=payload.expected_sign,
        image_blob=payload.image_blob,
        attempt_started_at=payload.attempt_started_at,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return PracticeAttemptSubmitResponse(
        attempt_id=str(attempt.attempt_id),
        message="Practice attempt recorded successfully",
    )


@router.post(
    "/assessment/attempt",
    response_model=AssessmentSubmitResponse,
    summary="Record word assessment",
)
def submit_assessment_attempt(
    payload: AssessmentSubmit,
    db: Session = Depends(get_db),
):
    """
    Record a word assessment result.

    - **session_id**: UUID of the practice session
    - **expected_sign**: The expected sign language gesture
    - **predicted_sign**: The AI-predicted sign language gesture
    - **confidence**: Confidence score 0.0 to 1.0
    """
    # Verify session exists
    session = (
        db.query(PracticeSession)
        .filter(PracticeSession.session_id == UUID(payload.session_id))
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found",
        )

    assessment = AssessmentAttempt(
        session_id=UUID(payload.session_id),
        expected_sign=payload.expected_sign,
        predicted_sign=payload.predicted_sign,
        confidence=payload.confidence,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return AssessmentSubmitResponse(
        assessment_id=str(assessment.assessment_id),
        message="Assessment recorded successfully",
    )

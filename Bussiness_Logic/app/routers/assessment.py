from fastapi import APIRouter, HTTPException
from app.schemas.assessment import AssessmentAttemptRequest, AssessmentOut
from app.services.assessment_service import assessment_store

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/attempt", response_model=AssessmentOut, status_code=201)
def record_attempt(payload: AssessmentAttemptRequest):
    assessment = assessment_store.record_attempt(
        session_id=payload.session_id,
        predicted_sign=payload.predicted_sign,
        expected_sign=payload.expected_sign,
        confidence=payload.confidence,
    )
    return assessment_store.to_out(assessment)


@router.get("/{session_id}", response_model=AssessmentOut)
def get_assessment(session_id: str):
    from uuid import UUID
    assessment = assessment_store.get(UUID(session_id))
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found for this session")
    return assessment_store.to_out(assessment)
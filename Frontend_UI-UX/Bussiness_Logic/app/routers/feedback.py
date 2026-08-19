from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.schemas.feedback import FeedbackGenerateRequest, FeedbackOut
from app.services.feedback_service import feedback_store
from app.services.assessment_service import assessment_store

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/generate", response_model=FeedbackOut, status_code=201)
def generate_feedback(payload: FeedbackGenerateRequest):
    assessment = assessment_store.get(payload.session_id)
    if assessment is None:
        raise HTTPException(
            status_code=404,
            detail="No assessment found for this session — record an attempt first"
        )
    assessment_out = assessment_store.to_out(assessment)
    feedback = feedback_store.generate(
        session_id=payload.session_id,
        assessment=assessment_out,
        expected_sign=payload.expected_sign,
        last_breakdown=assessment.last_breakdown,  # from Day 2's scoring breakdown
    )
    return feedback_store.to_out(feedback)


@router.get("/{session_id}", response_model=FeedbackOut)
def get_feedback(session_id: str):
    feedback = feedback_store.get(UUID(session_id))
    if feedback is None:
        raise HTTPException(status_code=404, detail="No feedback generated yet for this session")
    return feedback_store.to_out(feedback)
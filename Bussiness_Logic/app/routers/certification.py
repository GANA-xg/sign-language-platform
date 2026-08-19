from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from uuid import UUID
from typing import List, Union

from app.schemas.certification import (
    CertificationExamStartRequest,
    CertificationExamOut,
    CertificationAttemptRequest,
    CertificationAttemptResultOut,
    CertificationResultOut,
    CertificationLevelInfo,
    CertificationCertificateRequest,
)
from app.services.certification_service import certification_store, get_level_info
from app.services.certificate_service import generate_certification_certificate_pdf

router = APIRouter(prefix="/certification", tags=["certification"])


@router.get("/levels", response_model=List[CertificationLevelInfo])
def list_levels():
    return get_level_info()


@router.post("/start", response_model=CertificationExamOut, status_code=201)
def start_exam(payload: CertificationExamStartRequest):
    exam = certification_store.start_exam(payload.user_id, payload.level)
    return certification_store.to_out(exam)


@router.post("/attempt", response_model=CertificationAttemptResultOut)
def record_attempt(payload: CertificationAttemptRequest):
    try:
        exam = certification_store.record_attempt(
            exam_id=payload.exam_id,
            expected_sign=payload.expected_sign,
            predicted_sign=payload.predicted_sign,
            confidence=payload.confidence,
            hold_seconds=payload.hold_seconds,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    last_result = exam.attempt_results[-1]
    return certification_store.to_attempt_out(exam, last_result)


@router.post("/{exam_id}/complete", response_model=CertificationResultOut)
def complete_exam(exam_id: UUID):
    try:
        exam = certification_store.complete_exam(exam_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return certification_store.to_result_out(exam)


@router.get("/{exam_id}", response_model=Union[CertificationResultOut, CertificationExamOut])
def get_exam(exam_id: UUID):
    exam = certification_store.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Certification exam not found")
    if exam.status == "completed":
        return certification_store.to_result_out(exam)
    return certification_store.to_out(exam)


@router.get("/user/{user_id}/history", response_model=List[CertificationResultOut])
def get_exam_history(user_id: UUID):
    exams = certification_store.get_exams_by_user(user_id)
    completed = [e for e in exams if e.status == "completed"]
    return [certification_store.to_result_out(e) for e in completed]


@router.post("/{exam_id}/certificate")
def generate_exam_certificate(exam_id: UUID, payload: CertificationCertificateRequest):
    exam = certification_store.get(exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Certification exam not found")
    if exam.status != "completed":
        raise HTTPException(status_code=400, detail="Exam must be completed before issuing a certificate")
    if not exam.passed:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Learner did not pass this certification exam.",
                "score": exam.score,
                "pass_threshold": exam.pass_threshold,
            },
        )

    pdf_bytes, certificate_id = generate_certification_certificate_pdf(
        learner_name=payload.learner_name,
        level=exam.level,
        score=exam.score,
        accuracy_percentage=round(
            (exam.correct_predictions / exam.total_predictions * 100) if exam.total_predictions else 0.0, 2
        ),
        signs_covered=len(exam.required_signs),
    )
    certification_store.set_certificate_id(exam_id, certificate_id)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certification_{exam.level}_{certificate_id}.pdf"},
    )
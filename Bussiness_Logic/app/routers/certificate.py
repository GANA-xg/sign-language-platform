from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from uuid import UUID
from app.schemas.certificate import EligibilityOut, CertificateGenerateRequest
from app.services.certificate_service import check_eligibility, generate_certificate_pdf

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("/{user_id}/eligibility", response_model=EligibilityOut)
def get_eligibility(user_id: UUID):
    return check_eligibility(user_id)


@router.post("/{user_id}/generate")
def generate_certificate(user_id: UUID, payload: CertificateGenerateRequest):
    eligibility = check_eligibility(user_id)
    if not eligibility.eligible:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Learner does not meet certificate eligibility criteria.",
                "reasons_failed": eligibility.reasons_failed,
            }
        )

    pdf_bytes, certificate_id = generate_certificate_pdf(
        user_id=user_id,
        learner_name=payload.learner_name,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{certificate_id}.pdf"
        }
    )
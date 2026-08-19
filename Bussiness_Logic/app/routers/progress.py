from fastapi import APIRouter
from fastapi.responses import Response
from uuid import UUID
from app.schemas.progress import ProgressReportOut, ProgressReportPDFRequest
from app.services.progress_service import compute_progress_report, generate_progress_pdf

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{user_id}", response_model=ProgressReportOut)
def get_progress_report(user_id: UUID):
    return compute_progress_report(user_id)


@router.post("/{user_id}/pdf")
def get_progress_pdf(user_id: UUID, payload: ProgressReportPDFRequest):
    pdf_bytes = generate_progress_pdf(user_id, payload.learner_name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=progress_report_{user_id}.pdf"
        }
    )
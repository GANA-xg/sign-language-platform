from fastapi import APIRouter, Query
from fastapi.responses import Response
from uuid import UUID
from enum import Enum

from app.services.export_service import (
    generate_learner_progress_csv,
    generate_learner_progress_excel,
    generate_class_summary_csv,
    generate_class_summary_excel,
    generate_learning_report_pdf,
    generate_learning_report_excel,
    generate_assessment_report_pdf,
    generate_assessment_report_excel,
    generate_accuracy_report_pdf,
    generate_accuracy_report_excel,
    generate_certification_report_pdf,
    generate_certification_report_excel,
)

router = APIRouter(prefix="/export", tags=["export"])


class ExportFormat(str, Enum):
    csv = "csv"
    excel = "excel"
    pdf = "pdf"


@router.get("/{user_id}/progress")
def export_learner_progress(
    user_id: UUID,
    format: ExportFormat = Query(default=ExportFormat.csv)
):
    if format == ExportFormat.excel:
        data = generate_learner_progress_excel(user_id)
        return Response(content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=progress_{user_id}.xlsx"})
    data = generate_learner_progress_csv(user_id)
    return Response(content=data, media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=progress_{user_id}.csv"})


@router.get("/class/summary")
def export_class_summary(format: ExportFormat = Query(default=ExportFormat.csv)):
    if format == ExportFormat.excel:
        data = generate_class_summary_excel()
        return Response(content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=class_summary.xlsx"})
    data = generate_class_summary_csv()
    return Response(content=data, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=class_summary.csv"})


@router.get("/{user_id}/learning")
def export_learning_report(
    user_id: UUID,
    learner_name: str = Query(default="Learner"),
    format: ExportFormat = Query(default=ExportFormat.pdf)
):
    if format == ExportFormat.excel:
        data = generate_learning_report_excel(user_id)
        return Response(content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=learning_{user_id}.xlsx"})
    data = generate_learning_report_pdf(user_id, learner_name)
    return Response(content=data, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=learning_{user_id}.pdf"})


@router.get("/{user_id}/assessment")
def export_assessment_report(
    user_id: UUID,
    learner_name: str = Query(default="Learner"),
    format: ExportFormat = Query(default=ExportFormat.pdf)
):
    if format == ExportFormat.excel:
        data = generate_assessment_report_excel(user_id)
        return Response(content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=assessment_{user_id}.xlsx"})
    data = generate_assessment_report_pdf(user_id, learner_name)
    return Response(content=data, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=assessment_{user_id}.pdf"})


@router.get("/{user_id}/accuracy")
def export_accuracy_report(
    user_id: UUID,
    learner_name: str = Query(default="Learner"),
    format: ExportFormat = Query(default=ExportFormat.pdf)
):
    if format == ExportFormat.excel:
        data = generate_accuracy_report_excel(user_id)
        return Response(content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=accuracy_{user_id}.xlsx"})
    data = generate_accuracy_report_pdf(user_id, learner_name)
    return Response(content=data, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=accuracy_{user_id}.pdf"})


@router.get("/{user_id}/certification-report")
def export_certification_report(
    user_id: UUID,
    learner_name: str = Query(default="Learner"),
    format: ExportFormat = Query(default=ExportFormat.pdf)
):
    if format == ExportFormat.excel:
        data = generate_certification_report_excel(user_id)
        return Response(content=data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=certification_report_{user_id}.xlsx"})
    data = generate_certification_report_pdf(user_id, learner_name)
    return Response(content=data, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certification_report_{user_id}.pdf"})
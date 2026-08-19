import io
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.schemas.progress import ProgressReportOut
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.services.analytics_service import compute_weekly_analytics
from app.services.certificate_service import check_eligibility
from app.services.recommendation_service import get_recommendations
from app.schemas.practice import SessionStatus

WEAK_SIGN_THRESHOLD = 60.0
STRONG_SIGN_THRESHOLD = 80.0
WEAK_SIGN_MIN_ATTEMPTS = 2


def _grade_from_accuracy(accuracy: float) -> str:
    if accuracy >= 90: return "A"
    if accuracy >= 75: return "B"
    if accuracy >= 60: return "C"
    if accuracy >= 40: return "D"
    return "F"


def compute_progress_report(user_id: UUID) -> ProgressReportOut:
    sessions = practice_store.get_sessions_by_user(user_id)
    completed = [s for s in sessions if s.status == SessionStatus.completed]

    # Total practice time
    total_seconds = 0
    for s in sessions:
        if s.ended_at and s.started_at:
            total_seconds += int((s.ended_at - s.started_at).total_seconds())

    # Aggregate sign stats
    accuracies: List[float] = []
    combined_sign_stats: Dict[str, Dict[str, int]] = {}

    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment is None or assessment.total_predictions == 0:
            continue
        accuracies.append(
            assessment.correct_predictions / assessment.total_predictions * 100
        )
        for sign, stats in assessment.sign_stats.items():
            entry = combined_sign_stats.setdefault(sign, {"correct": 0, "total": 0})
            entry["correct"] += stats["correct"]
            entry["total"] += stats["total"]

    average_accuracy = round(sum(accuracies) / len(accuracies), 2) if accuracies else 0.0

    weak_signs = [
        sign for sign, stats in combined_sign_stats.items()
        if stats["total"] >= WEAK_SIGN_MIN_ATTEMPTS
        and (stats["correct"] / stats["total"] * 100) < WEAK_SIGN_THRESHOLD
    ]
    strong_signs = [
        sign for sign, stats in combined_sign_stats.items()
        if stats["total"] >= WEAK_SIGN_MIN_ATTEMPTS
        and (stats["correct"] / stats["total"] * 100) >= STRONG_SIGN_THRESHOLD
    ]

    # Weekly data
    weekly = compute_weekly_analytics(user_id)

    # Certificate eligibility
    eligibility = check_eligibility(user_id)

    # Recommendations
    recs = get_recommendations(user_id)
    recommended_signs = [r.sign for r in recs.recommendations]

    return ProgressReportOut(
        user_id=user_id,
        generated_at=datetime.now(timezone.utc),
        total_sessions=len(sessions),
        completed_sessions=len(completed),
        total_practice_time_seconds=total_seconds,
        average_accuracy=average_accuracy,
        grade=_grade_from_accuracy(average_accuracy),
        distinct_signs_practiced=len(combined_sign_stats),
        weak_signs=weak_signs,
        strong_signs=strong_signs,
        current_week_accuracy=weekly.current_week_accuracy,
        improvement_rate=weekly.improvement_rate,
        recommended_for_practice=recommended_signs,
        certificate_eligible=eligibility.eligible,
        certificate_reasons_failed=eligibility.reasons_failed,
    )


def generate_progress_pdf(user_id: UUID, learner_name: str) -> bytes:
    report = compute_progress_report(user_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2.5*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=22,
        textColor=colors.HexColor("#1a237e"), alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle("subtitle", parent=styles["Normal"], fontSize=11,
        textColor=colors.HexColor("#37474f"), alignment=TA_CENTER, spaceAfter=16)
    section_style = ParagraphStyle("section", parent=styles["Normal"], fontSize=13,
        textColor=colors.HexColor("#1565c0"), fontName="Helvetica-Bold", spaceAfter=8)
    body_style = ParagraphStyle("body", parent=styles["Normal"], fontSize=11,
        alignment=TA_LEFT, spaceAfter=6)
    small_style = ParagraphStyle("small", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#78909c"), alignment=TA_CENTER, spaceAfter=4)

    minutes = report.total_practice_time_seconds // 60
    cert_status = "✓ Eligible" if report.certificate_eligible else "✗ Not yet eligible"

    story = [
        Paragraph("PROGRESS REPORT", title_style),
        Paragraph("AI-Powered Sign Language Learning Platform", subtitle_style),
        Paragraph(f"Learner: {learner_name}", subtitle_style),
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a237e"), spaceAfter=16),

        # Overview
        Paragraph("Overview", section_style),
        Paragraph(f"Total Sessions: <b>{report.total_sessions}</b> "
                  f"(Completed: <b>{report.completed_sessions}</b>)", body_style),
        Paragraph(f"Total Practice Time: <b>{minutes} minutes</b>", body_style),
        Paragraph(f"Average Accuracy: <b>{report.average_accuracy}%</b> "
                  f"(Grade: <b>{report.grade}</b>)", body_style),
        Paragraph(f"Distinct Signs Practiced: <b>{report.distinct_signs_practiced}</b>", body_style),
        Spacer(1, 0.5*cm),

        # Signs breakdown
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0"), spaceAfter=12),
        Paragraph("Signs Breakdown", section_style),
        Paragraph(
            f"Strong Signs (≥80%): <b>{', '.join(report.strong_signs) if report.strong_signs else 'None yet'}</b>",
            body_style),
        Paragraph(
            f"Weak Signs (<60%): <b>{', '.join(report.weak_signs) if report.weak_signs else 'None'}</b>",
            body_style),
        Paragraph(
            f"Recommended for extra practice: <b>{', '.join(report.recommended_for_practice) if report.recommended_for_practice else 'None'}</b>",
            body_style),
        Spacer(1, 0.5*cm),

        # Weekly
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0"), spaceAfter=12),
        Paragraph("This Week", section_style),
        Paragraph(
            f"Current Week Accuracy: <b>{report.current_week_accuracy}%</b>" if report.current_week_accuracy else "Current Week Accuracy: <b>No data yet</b>",
            body_style),
        Paragraph(
            f"Improvement Rate: <b>{report.improvement_rate}%</b>" if report.improvement_rate else "Improvement Rate: <b>Not enough weeks yet</b>",
            body_style),
        Spacer(1, 0.5*cm),

        # Certificate
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0"), spaceAfter=12),
        Paragraph("Certificate Status", section_style),
        Paragraph(f"Status: <b>{cert_status}</b>", body_style),
    ]

    if not report.certificate_eligible and report.certificate_reasons_failed:
        story.append(Paragraph("To qualify, you still need to:", body_style))
        for reason in report.certificate_reasons_failed:
            story.append(Paragraph(f"• {reason}", body_style))

    story += [
        Spacer(1, 1*cm),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e0e0e0"), spaceAfter=8),
        Paragraph(f"Report generated: {report.generated_at.strftime('%B %d, %Y at %H:%M UTC')}", small_style),
        Paragraph("AI Sign Language Platform — Infosys Springboard", small_style),
    ]

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
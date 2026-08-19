import io
import uuid as uuid_module
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Tuple, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


from app.schemas.certificate import EligibilityOut
from app.services.practice_service import practice_store
from app.services.assessment_service import assessment_store
from app.schemas.practice import SessionStatus

# ── Certificate eligibility rules ────────────────────────────────────
# Adjust these constants to tune difficulty without touching logic.
MIN_COMPLETED_SESSIONS = 1
MIN_AVERAGE_ACCURACY = 80.0
MIN_DISTINCT_SIGNS = 1
MAX_WEAK_SIGNS = 2          # learner can have at most this many weak signs
WEAK_SIGN_THRESHOLD = 60.0
WEAK_SIGN_MIN_ATTEMPTS = 2


def check_eligibility(user_id: UUID) -> EligibilityOut:
    sessions = practice_store.get_sessions_by_user(user_id)

    completed_sessions = [
        s for s in sessions if s.status == SessionStatus.completed
    ]

    # Aggregate cross-session stats
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

    average_accuracy = (sum(accuracies) / len(accuracies)) if accuracies else 0.0
    distinct_signs = len(combined_sign_stats)
    weak_signs = [
        sign for sign, stats in combined_sign_stats.items()
        if stats["total"] >= WEAK_SIGN_MIN_ATTEMPTS
        and (stats["correct"] / stats["total"] * 100) < WEAK_SIGN_THRESHOLD
    ]

    # ── Check each rule ───────────────────────────────────────────────
    reasons_failed: List[str] = []
    criteria_met: List[str] = []

    # Rule 1: completed sessions
    if len(completed_sessions) >= MIN_COMPLETED_SESSIONS:
        criteria_met.append(
            f"Completed sessions: {len(completed_sessions)} (required: {MIN_COMPLETED_SESSIONS})"
        )
    else:
        reasons_failed.append(
            f"Not enough completed sessions: {len(completed_sessions)}/{MIN_COMPLETED_SESSIONS}"
        )

    # Rule 2: average accuracy
    if average_accuracy >= MIN_AVERAGE_ACCURACY:
        criteria_met.append(
            f"Average accuracy: {round(average_accuracy, 1)}% (required: {MIN_AVERAGE_ACCURACY}%)"
        )
    else:
        reasons_failed.append(
            f"Average accuracy too low: {round(average_accuracy, 1)}% (required: {MIN_AVERAGE_ACCURACY}%)"
        )

    # Rule 3: distinct signs practiced
    if distinct_signs >= MIN_DISTINCT_SIGNS:
        criteria_met.append(
            f"Distinct signs practiced: {distinct_signs} (required: {MIN_DISTINCT_SIGNS})"
        )
    else:
        reasons_failed.append(
            f"Not enough distinct signs practiced: {distinct_signs}/{MIN_DISTINCT_SIGNS}"
        )

    # Rule 4: weak signs
    if len(weak_signs) <= MAX_WEAK_SIGNS:
        criteria_met.append(
            f"Weak signs: {len(weak_signs)} (allowed: up to {MAX_WEAK_SIGNS})"
        )
    else:
        reasons_failed.append(
            f"Too many weak signs: {len(weak_signs)} (allowed: up to {MAX_WEAK_SIGNS}). "
            f"Practice more: {', '.join(weak_signs)}"
        )

    return EligibilityOut(
        user_id=user_id,
        eligible=len(reasons_failed) == 0,
        reasons_failed=reasons_failed,
        criteria_met=criteria_met,
        checked_at=datetime.now(timezone.utc),
    )



def generate_certificate_pdf(
    user_id: UUID,
    learner_name: str,
) -> tuple[bytes, str]:
    """
    Generates a certificate PDF in memory.
    Returns (pdf_bytes, certificate_id).
    Caller is responsible for checking eligibility first.
    """
    # Gather stats for the certificate
    sessions = practice_store.get_sessions_by_user(user_id)
    completed_sessions = [s for s in sessions if s.status == SessionStatus.completed]

    accuracies = []
    sign_stats: Dict[str, Dict[str, int]] = {}
    for session in sessions:
        assessment = assessment_store.get(session.session_id)
        if assessment is None or assessment.total_predictions == 0:
            continue
        accuracies.append(
            assessment.correct_predictions / assessment.total_predictions * 100
        )
        for sign, stats in assessment.sign_stats.items():
            entry = sign_stats.setdefault(sign, {"correct": 0, "total": 0})
            entry["correct"] += stats["correct"]
            entry["total"] += stats["total"]

    average_accuracy = round(sum(accuracies) / len(accuracies), 2) if accuracies else 0.0
    distinct_signs = len(sign_stats)
    certificate_id = str(uuid_module.uuid4())[:8].upper()
    issued_at = datetime.now(timezone.utc)

    # Build PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=3*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    centered = ParagraphStyle(
        "centered",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=28,
        textColor=colors.HexColor("#1a237e"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "subtitle",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.HexColor("#37474f"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    name_style = ParagraphStyle(
        "name",
        parent=styles["Normal"],
        fontSize=26,
        textColor=colors.HexColor("#1565c0"),
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=16,
    )
    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    small_style = ParagraphStyle(
        "small",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#78909c"),
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    story = [
        Spacer(1, 1*cm),
        Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style),
        Paragraph("AI-Powered Sign Language Learning Platform", subtitle_style),
        HRFlowable(width="80%", thickness=2, color=colors.HexColor("#1a237e"), spaceAfter=20),
        Spacer(1, 0.5*cm),
        Paragraph("This is to certify that", body_style),
        Spacer(1, 0.3*cm),
        Paragraph(learner_name, name_style),
        Spacer(1, 0.3*cm),
        Paragraph(
            "has successfully completed the Sign Language Practice Programme "
            "and demonstrated proficiency in American Sign Language (ASL) hand signs.",
            body_style,
        ),
        Spacer(1, 0.8*cm),
        HRFlowable(width="60%", thickness=1, color=colors.HexColor("#90a4ae"), spaceAfter=16),
        Paragraph(f"Average Accuracy: <b>{average_accuracy}%</b>", body_style),
        Paragraph(f"Sessions Completed: <b>{len(completed_sessions)}</b>", body_style),
        Paragraph(f"Signs Practiced: <b>{distinct_signs}</b>", body_style),
        Spacer(1, 0.8*cm),
        HRFlowable(width="60%", thickness=1, color=colors.HexColor("#90a4ae"), spaceAfter=16),
        Paragraph(f"Date Issued: <b>{issued_at.strftime('%B %d, %Y')}</b>", body_style),
        Spacer(1, 1.5*cm),
        Paragraph(f"Certificate ID: {certificate_id}", small_style),
        Paragraph("Issued by: AI Sign Language Platform — Infosys Springboard", small_style),
    ]

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes, certificate_id
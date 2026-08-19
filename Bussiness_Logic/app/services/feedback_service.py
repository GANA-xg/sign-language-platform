from uuid import UUID
from datetime import datetime, timezone
from typing import Dict, Optional, List

from app.models.feedback import SessionFeedback
from app.schemas.feedback import FeedbackItem, FeedbackType, Severity, FeedbackOut
from app.schemas.assessment import AssessmentOut


# ─────────────────────────────────────────────
# Per-sign tip bank (covers A–O, 15 signs)
# Expanded when Abhinaya's model grows further.
# Each entry: (correction_tip, praise_tip)
# ─────────────────────────────────────────────
SIGN_TIPS: Dict[str, Dict[str, str]] = {
    "A": {
        "correction": "For A: make a fist with your thumb resting on the side — don't let it cross over your fingers.",
        "praise": "Clean A — fist shape and thumb position were spot on.",
    },
    "B": {
        "correction": "For B: hold four fingers straight up together, thumb tucked flat across your palm.",
        "praise": "Great B — fingers straight and thumb tucked correctly.",
    },
    "C": {
        "correction": "For C: curve all fingers and thumb together into a C shape — avoid closing them too far into a fist.",
        "praise": "Nice C — the curve looked natural and open.",
    },
    "D": {
        "correction": "For D: index finger points up, other fingers and thumb form a circle touching it.",
        "praise": "Good D — index finger and circle shape were clear.",
    },
    "E": {
        "correction": "For E: curl all fingers down so their tips touch your thumb — keep the curl tight.",
        "praise": "Solid E — fingers curled correctly.",
    },
    "F": {
        "correction": "For F: touch your index finger to your thumb to make a circle, other three fingers up.",
        "praise": "Nice F — the circle and raised fingers were clear.",
    },
    "G": {
        "correction": "For G: point index finger sideways and thumb parallel to it — keep them horizontal, not angled up.",
        "praise": "Good G — horizontal index and thumb alignment was correct.",
    },
    "H": {
        "correction": "For H: extend index and middle fingers sideways together, horizontally.",
        "praise": "Clean H — two fingers extended horizontally, well done.",
    },
    "I": {
        "correction": "For I: raise only your pinky finger straight up, all other fingers in a fist.",
        "praise": "Great I — pinky isolated cleanly.",
    },
    "J": {
        "correction": "For J: start like I (pinky up) then draw a J shape in the air — the motion matters.",
        "praise": "Good J — pinky and the J motion were both clear.",
    },
    "K": {
        "correction": "For K: index finger up, middle finger angled out, thumb between them — spread them clearly.",
        "praise": "Good K — the three-finger spread was clear.",
    },
    "L": {
        "correction": "For L: extend your index finger up and thumb out sideways — make a clear right-angle L shape.",
        "praise": "Nice L — the right-angle shape was clean.",
    },
    "M": {
        "correction": "For M: tuck your thumb under three fingers (index, middle, ring) folded over it.",
        "praise": "Good M — three fingers over thumb looked correct.",
    },
    "N": {
        "correction": "For N: tuck thumb under two fingers (index and middle) folded over it.",
        "praise": "Clean N — two fingers over thumb was right.",
    },
    "O": {
        "correction": "For O: curve all fingers and thumb to touch at the tips, forming a clear O circle.",
        "praise": "Great O — the circular shape was well formed.",
    },
    "P": {
        "correction": "For P: like K but pointed downward — index finger points down, middle finger out, thumb between.",
        "praise": "Good P — downward K shape was correct.",
    },
    "Q": {
        "correction": "For Q: like G but pointed downward — index and thumb pointing down together.",
        "praise": "Nice Q — downward G orientation was right.",
    },
    "R": {
        "correction": "For R: cross your index and middle fingers while extending them up together.",
        "praise": "Good R — crossed fingers were clearly visible.",
    },
    "S": {
        "correction": "For S: make a fist with your thumb crossing over your fingers — different from A where thumb is on the side.",
        "praise": "Clean S — fist with thumb over fingers was correct.",
    },
    "T": {
        "correction": "For T: make a fist with your thumb tucked between index and middle fingers.",
        "praise": "Good T — thumb between index and middle fingers was right.",
    },
    "U": {
        "correction": "For U: extend index and middle fingers straight up together, side by side.",
        "praise": "Nice U — two fingers straight up and together.",
    },
    "V": {
        "correction": "For V: extend index and middle fingers in a V shape (spread apart), thumb holding other fingers.",
        "praise": "Great V — the spread between index and middle fingers was clear.",
    },
    "W": {
        "correction": "For W: extend index, middle, and ring fingers spread apart in a W shape.",
        "praise": "Good W — three fingers spread correctly.",
    },
    "X": {
        "correction": "For X: extend and bend your index finger into a hook shape.",
        "praise": "Nice X — the hooked index finger was clear.",
    },
    "Y": {
        "correction": "For Y: extend thumb and pinky out, keep other three fingers folded in tightly.",
        "praise": "Nice Y — thumb and pinky extension was clear.",
    },
    "Z": {
        "correction": "For Z: extend your index finger and draw a Z shape in the air.",
        "praise": "Good Z — index finger and Z motion were both visible.",
    },
}

GENERIC_CORRECTION = "Check your hand shape carefully against the reference image and try again."
GENERIC_PRAISE = "Great job! Your sign was accurate."

# Ideal hold duration range in seconds (matches scoring_service.py)
IDEAL_DURATION_LOW = 0.8
IDEAL_DURATION_HIGH = 3.0


def generate_feedback_items(
    assessment: AssessmentOut,
    expected_sign: Optional[str] = None,
    last_breakdown: Optional[dict] = None,
    possible_issue: Optional[str] = None,
) -> List[FeedbackItem]:
    items: List[FeedbackItem] = []
    score = assessment.score
    accuracy = assessment.accuracy_percentage
    sign = expected_sign.upper() if expected_sign else None
    tips = SIGN_TIPS.get(sign, {}) if sign else {}
    if possible_issue:
        items.append(FeedbackItem(
            feedback_type=FeedbackType.improvement,
            message=f"AI detected a possible issue: {possible_issue}",
            severity=Severity.medium,
        ))
    # ── 1. Primary score-based feedback ──────────────────────────────
    if score >= 85:
        items.append(FeedbackItem(
            feedback_type=FeedbackType.praise,
            message=tips.get("praise", GENERIC_PRAISE),
            severity=Severity.low,
        ))
    elif score >= 60:
        items.append(FeedbackItem(
            feedback_type=FeedbackType.improvement,
            message=tips.get("correction", GENERIC_CORRECTION),
            severity=Severity.medium,
        ))
    else:
        items.append(FeedbackItem(
            feedback_type=FeedbackType.correction,
            message=tips.get("correction", GENERIC_CORRECTION),
            severity=Severity.high,
        ))

    # ── 2. Duration-specific feedback (from Day 2 breakdown) ─────────
    if last_breakdown and "duration" in last_breakdown.get("components", {}):
        duration_score = last_breakdown["components"]["duration"]
        hold = last_breakdown.get("hold_seconds")

        if hold is not None and hold < IDEAL_DURATION_LOW:
            items.append(FeedbackItem(
                feedback_type=FeedbackType.improvement,
                message=f"You held the sign for only {hold:.1f}s — try holding it for at least 1 second so the camera can capture it clearly.",
                severity=Severity.medium,
            ))
        elif hold is not None and hold > IDEAL_DURATION_HIGH:
            items.append(FeedbackItem(
                feedback_type=FeedbackType.improvement,
                message=f"You held the sign for {hold:.1f}s — aim for 1–3 seconds for the best score.",
                severity=Severity.low,
            ))

    # ── 3. Low accuracy across the session ───────────────────────────
    if accuracy < 50 and assessment.total_predictions > 0:
        items.append(FeedbackItem(
            feedback_type=FeedbackType.correction,
            message="You're missing more than half your attempts — slow down and review the reference sign before each try.",
            severity=Severity.high,
        ))

    return items


class InMemoryFeedbackStore:
    def __init__(self):
        self._feedback: Dict[UUID, SessionFeedback] = {}

    def generate(
        self,
        session_id: UUID,
        assessment: AssessmentOut,
        expected_sign: Optional[str] = None,
        last_breakdown: Optional[dict] = None,
        possible_issue: Optional[str] = None,
    ) -> SessionFeedback:
        items = generate_feedback_items(assessment, expected_sign, last_breakdown)
        feedback = SessionFeedback(
            session_id=session_id,
            items=items,
            generated_at=datetime.now(timezone.utc),
        )
        self._feedback[session_id] = feedback
        return feedback

    def get(self, session_id: UUID) -> Optional[SessionFeedback]:
        return self._feedback.get(session_id)

    def to_out(self, feedback: SessionFeedback) -> FeedbackOut:
        return FeedbackOut(
            session_id=feedback.session_id,
            feedback=feedback.items,
            generated_at=feedback.generated_at,
        )


feedback_store = InMemoryFeedbackStore()
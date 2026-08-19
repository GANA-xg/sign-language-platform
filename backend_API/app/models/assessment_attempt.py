from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, TIMESTAMP, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("practice_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expected_sign: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_sign: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    assessed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AssessmentAttempt {self.assessment_id} for session {self.session_id}>"

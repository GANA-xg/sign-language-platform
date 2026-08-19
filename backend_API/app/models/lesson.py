from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.module import Module  # only for type-checking, not runtime

class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "sequence_order", name="uq_lessons_module_seq"),
        CheckConstraint(
            "difficulty_level IN ('beginner','intermediate','advanced')",
            name="chk_lessons_difficulty",
        ),
        CheckConstraint(
            "estimated_duration_minutes IS NULL OR estimated_duration_minutes > 0",
            name="chk_lessons_duration",
        ),
    )

    lesson_id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(
        ForeignKey("modules.module_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'beginner'"))
    category: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'Alphabet'"))
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    # updated_at kept fresh by DB trigger trg_lessons_updated_at — don't set manually.

    module: Mapped["Module"] = relationship(back_populates="lessons")

    def __repr__(self) -> str:
        return f"<Lesson {self.title}>"
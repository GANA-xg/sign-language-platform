from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING

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

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.sign_language import SignLanguage


class Module(Base):
    __tablename__ = "modules"

    __table_args__ = (
        UniqueConstraint(
            "sign_language_id",
            "sequence_order",
            name="uq_modules_lang_seq",
        ),
        CheckConstraint(
            "difficulty_level IN ('beginner','intermediate','advanced')",
            name="chk_modules_difficulty",
        ),
    )

    module_id: Mapped[int] = mapped_column(primary_key=True)

    sign_language_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sign_languages.sign_language_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    difficulty_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'beginner'")
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false")
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sign_language: Mapped["SignLanguage"] = relationship(
        back_populates="modules"
    )

    lessons: Mapped[List["Lesson"]] = relationship(
        back_populates="module"
    )

    def __repr__(self):
        return f"<Module {self.title}>"
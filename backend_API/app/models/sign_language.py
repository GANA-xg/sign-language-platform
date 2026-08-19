from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.module import Module
class SignLanguage(Base):
    __tablename__ = "sign_languages"

    sign_language_id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    modules: Mapped[List["Module"]] = relationship(back_populates="sign_language")

    def __repr__(self) -> str:
        return f"<SignLanguage {self.code}>"
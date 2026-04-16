from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Импортируем Base из общего файла (обычно он в db_ext.py или base.py)
from .user import Base

if TYPE_CHECKING:
    from .user import User


class TestSubmission(Base):
    __tablename__ = "test_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)

    # Рекомендуется использовать server_default=func.now() для точности на стороне БД
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Отношение к пользователю
    student: Mapped["User"] = relationship("User", back_populates="test_submissions")

    __table_args__ = (
        CheckConstraint("length(title) >= 3", name="ck_submission_title_length"),
        CheckConstraint("length(topic) >= 2", name="ck_submission_topic_length"),
    )
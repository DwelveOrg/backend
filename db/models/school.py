from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.user import User


class SchoolTeacher(Base):
    """Связь школа↔учитель"""
    __tablename__ = "school_teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    school: Mapped["User"] = relationship("User", foreign_keys=[school_id], back_populates="my_teachers")
    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id], back_populates="my_schools")

    __table_args__ = (
        UniqueConstraint("school_id", "teacher_id", name="uq_school_teacher"),
    )
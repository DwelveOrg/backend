from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, func, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.assignment import Assignment


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    graded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    grader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    assignment: Mapped["Assignment"] = relationship("Assignment", back_populates="grades")
    student: Mapped["User"] = relationship("User", foreign_keys=[student_id], back_populates="grades_received")
    grader: Mapped["User"] = relationship("User", foreign_keys=[grader_id], back_populates="grades_given")

    __table_args__ = (
        UniqueConstraint("assignment_id", "student_id", name="uq_assignment_student"),
    )
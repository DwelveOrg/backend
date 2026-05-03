from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING
from enum import Enum


from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.study_group import StudyGroup
    from db.models.grade import Grade


class AssignmentStatus(str, Enum):
    pending = "pending"      # не сдано
    submitted = "submitted"  # сдано учеником
    graded = "graded"        # оценено учителем


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("study_groups.id"), nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    group: Mapped["StudyGroup"] = relationship("StudyGroup", back_populates="assignments")
    creator: Mapped["User"] = relationship("User", back_populates="assignments_created")
    grades: Mapped[List["Grade"]] = relationship(
        "Grade",
        back_populates="assignment",
        cascade="all, delete-orphan"
    )
    submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission",
        back_populates="assignment",
        cascade="all, delete-orphan"
    )


class AssignmentSubmission(Base):
    """Сдача задания учеником"""
    __tablename__ = "assignment_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(
        String(20), default=AssignmentStatus.pending, nullable=False
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    assignment: Mapped["Assignment"] = relationship("Assignment", back_populates="submissions")
    student: Mapped["User"] = relationship("User", back_populates="assignment_submissions")
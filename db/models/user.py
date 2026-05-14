from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from app.core.security import pwd_context

if TYPE_CHECKING:
    from db.models.submission import TestSubmission
    from db.models.membership import GroupMembership
    from db.models.study_group import StudyGroup
    from db.models.assignment import Assignment
    from db.models.grade import Grade
    from db.models.assignment import AssignmentSubmission
    from db.models.school import SchoolTeacher


class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    school = "school"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    paid_member: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), default=UserRole.student, nullable=False)

    test_submissions: Mapped[List["TestSubmission"]] = relationship(
        "TestSubmission",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    groups_led: Mapped[List["StudyGroup"]] = relationship(
        "StudyGroup",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    assignments_created: Mapped[List["Assignment"]] = relationship(
        "Assignment",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    grades_received: Mapped[List["Grade"]] = relationship(
        "Grade",
        foreign_keys="Grade.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    grades_given: Mapped[List["Grade"]] = relationship(
        "Grade",
        foreign_keys="Grade.grader_id",
        back_populates="grader",
        cascade="all, delete-orphan",
    )
    assignment_submissions: Mapped[List["AssignmentSubmission"]] = relationship(
        "AssignmentSubmission",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    my_teachers: Mapped[List["SchoolTeacher"]] = relationship(
        "SchoolTeacher",
        foreign_keys="SchoolTeacher.school_id",
        back_populates="school",
        cascade="all, delete-orphan",
    )
    my_schools: Mapped[List["SchoolTeacher"]] = relationship(
        "SchoolTeacher",
        foreign_keys="SchoolTeacher.teacher_id",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )

    @property
    def is_teacher(self) -> bool:
        return self.role == UserRole.teacher

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.student

    @property
    def is_school(self) -> bool:
        return self.role == UserRole.school

    @property
    def can_create_groups(self) -> bool:
        """Учителя и школы могут создавать группы"""
        return self.role in (UserRole.teacher, UserRole.school)

    def set_password(self, password: str) -> None:
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
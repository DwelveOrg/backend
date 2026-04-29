from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING
from enum import Enum

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, CheckConstraint, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from db.base import Base

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.membership import GroupMembership
    from db.models.assignment import Assignment


class GroupType(str, Enum):
    student = "student"   # группа для учеников
    teacher = "teacher"   # группа для учителей
    mixed = "mixed"       # смешанная группа


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    tutor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    group_type: Mapped[str] = mapped_column(
        String(20), default=GroupType.student, nullable=False
    )

    capacity: Mapped[int] = mapped_column(default=25, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="groups_led")
    memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("capacity >= 2", name="ck_group_capacity_min"),
        CheckConstraint("length(name) >= 3", name="ck_group_name_length"),
    )
    assignments: Mapped[List["Assignment"]] = relationship(
        "Assignment",
        back_populates="group",
        cascade="all, delete-orphan"
    )


from db.models.membership import GroupMembership  # noqa: E402

StudyGroup.member_count = column_property(
    select(func.count(GroupMembership.id))
    .where(GroupMembership.group_id == StudyGroup.id)
    .correlate_except(GroupMembership)
    .scalar_subquery()
)
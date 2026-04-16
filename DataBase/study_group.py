from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, CheckConstraint, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .user import Base

if TYPE_CHECKING:
    from .user import User
    from .membership import GroupMembership

class StudyGroup(Base):
    __tablename__ = "study_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    subject: Mapped[str] = mapped_column(String(120), nullable=False)
    tutor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    capacity: Mapped[int] = mapped_column(default=25, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Отношения
    owner: Mapped["User"] = relationship("User", back_populates="groups_led")
    memberships: Mapped[List["GroupMembership"]] = relationship(
        "GroupMembership",
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin"  # Оставляем selectin для удобства подгрузки
    )

    __table_args__ = (
        CheckConstraint("capacity >= 2", name="ck_group_capacity_min"),
        CheckConstraint("length(name) >= 3", name="ck_group_name_length"),
    )

    # Важное замечание по member_count:
    # В FastAPI/SQLAlchemy 2.0 лучше считать это в репозитории или
    # через column_property, чтобы избежать лишних запросов.
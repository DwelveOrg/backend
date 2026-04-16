from __future__ import annotations
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

# Используем passlib для хеширования (стандарт для FastAPI)
from passlib.context import CryptContext

# Чтобы избежать цикличных импортов при типизации
if TYPE_CHECKING:
    from .submission import TestSubmission
    from .membership import GroupMembership
    from .study_group import StudyGroup

# Настройка контекста паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Base(DeclarativeBase):
    pass


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

    role: Mapped[str] = mapped_column(String(20), default="student", nullable=False)

    # Отношения (Relationships)
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

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    # Методы безопасности
    def set_password(self, password: str) -> None:
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
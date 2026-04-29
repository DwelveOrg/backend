from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Literal
from db.models.user import UserRole
from db.models.study_group import GroupType
from datetime import datetime


class MsgResponse(BaseModel):
    message: str


class RegisterStart(BaseModel):
    full_name: str = Field(..., min_length=5)
    email: EmailStr
    role: UserRole  # ← теперь Enum вместо Literal


class RegisterVerify(BaseModel):
    email: EmailStr
    code: str


class RegisterComplete(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    accept_terms: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GroupShortInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    subject: str
    member_count: int


class UserBaseInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: str
    paid_member: bool


class SubmissionShortInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    topic: str
    # TODO: добавить score, submitted_at и др. когда будет модель


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3)
    subject: str
    tutor_name: str
    description: str
    capacity: int = Field(25, ge=2)
    is_private: bool = False
    group_type: GroupType = GroupType.student


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class GroupListResponse(BaseModel):
    groups: List[GroupShortInfo]
    pagination: PaginationMeta


class TestSubmissionCreate(BaseModel):
    title: str = Field(..., min_length=3)
    topic: str = Field(..., min_length=2)
    notes: str = Field(..., min_length=10)

class AssignmentCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str = Field(..., min_length=10)
    due_date: datetime | None = None


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    due_date: datetime | None
    created_at: datetime
    group_id: int
    creator_id: int


class GradeCreate(BaseModel):
    student_id: int
    score: float = Field(..., ge=0, le=100)
    comment: str | None = None


class GradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    score: float
    comment: str | None
    graded_at: datetime
    assignment_id: int
    student_id: int
    grader_id: int

class DashboardResponse(BaseModel):
    user: UserBaseInfo
    # Для учителя/школы
    groups_created: Optional[List[GroupShortInfo]] = None
    assignments_created: Optional[List[AssignmentResponse]] = None
    # Для студента
    groups_joined: Optional[List[GroupShortInfo]] = None
    submissions: Optional[List[SubmissionShortInfo]] = None
    assignments: Optional[List[AssignmentResponse]] = None
    grades: Optional[List[GradeResponse]] = None

class UserUpdateProfile(BaseModel):
    full_name: str | None = Field(None, min_length=5)


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
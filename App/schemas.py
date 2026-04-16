from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class MsgResponse(BaseModel):
    message: str

class RegisterStart(BaseModel):
    full_name: str = Field(..., min_length=5)
    email: EmailStr
    role: str # Можно сделать Literal["student", "teacher"]

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
    id: int
    name: str
    subject: str
    member_count: int

    class Config:
        from_attributes = True

class UserBaseInfo(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    paid_member: bool

class DashboardResponse(BaseModel):
    user: UserBaseInfo
    groups_created: Optional[List[GroupShortInfo]] = None
    groups_joined: Optional[List[GroupShortInfo]] = None
    submissions: Optional[List[dict]] = None # Можно детализировать позже

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3)
    subject: str
    tutor_name: str
    description: str
    capacity: int = Field(25, ge=2)
    is_private: bool = False

class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class GroupListResponse(BaseModel):
    groups: List[GroupShortInfo] # Используем созданную ранее схему
    pagination: PaginationMeta

class TestSubmissionCreate(BaseModel):
    title: str = Field(..., min_length=3)
    topic: str = Field(..., min_length=2)
    notes: str = Field(..., min_length=10)
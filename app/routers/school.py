from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from app.core.security import pwd_context

from db.db_ext import get_db
from db.models.user import User, UserRole
from db.models.study_group import StudyGroup
from db.models.membership import GroupMembership
from db.models.school import SchoolTeacher
from app.schemas import UserBaseInfo, RegisterStart, MsgResponse, SchoolRegister
from app.dependencies.auth_deps import get_current_user, role_required

router = APIRouter(prefix="/school", tags=["school"])
SCHOOL_SECRET_KEY = os.getenv("SCHOOL_SECRET_KEY", "school-secret-change-in-production")

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_school(
    payload: SchoolRegister,
    db: AsyncSession = Depends(get_db)
):
    """Регистрация школы через секретный ключ"""
    if payload.secret_key != SCHOOL_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret key.")

    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists.")

    school = User(
        full_name=payload.full_name,
        email=payload.email,
        role=UserRole.school
    )
    school.set_password(payload.password)
    db.add(school)
    await db.commit()
    return {"message": "School registered successfully."}

@router.get("/teachers", response_model=list[UserBaseInfo])
async def list_teachers(
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Список всех учителей"""
    result = await db.execute(
        select(User).where(User.role == UserRole.teacher)
    )
    return result.scalars().all()


@router.get("/students", response_model=list[UserBaseInfo])
async def list_students(
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Список всех учеников"""
    result = await db.execute(
        select(User).where(User.role == UserRole.student)
    )
    return result.scalars().all()


@router.get("/groups", response_model=list)
async def list_all_groups(
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Все группы школы"""
    result = await db.execute(select(StudyGroup))
    groups = result.scalars().all()
    return [
        {
            "id": g.id,
            "name": g.name,
            "subject": g.subject,
            "group_type": g.group_type,
            "capacity": g.capacity,
            "owner_id": g.owner_id,
        }
        for g in groups
    ]


@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Школа может менять роль пользователя"""
    if new_role == UserRole.school:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign school role."
        )

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role.")

    user.role = new_role
    await db.commit()
    await db.refresh(user)
    return {"message": f"Role updated to {new_role}.", "user_id": user_id}


@router.get("/stats")
async def school_stats(
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Статистика школы"""
    teachers = await db.execute(select(User).where(User.role == UserRole.teacher))
    students = await db.execute(select(User).where(User.role == UserRole.student))
    groups = await db.execute(select(StudyGroup))

    return {
        "total_teachers": len(teachers.scalars().all()),
        "total_students": len(students.scalars().all()),
        "total_groups": len(groups.scalars().all()),
    }

@router.post("/teachers/{teacher_id}", status_code=status.HTTP_201_CREATED)
async def add_teacher(
    teacher_id: int,
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Школа добавляет учителя"""
    teacher = await db.get(User, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="User not found.")

    if teacher.role != UserRole.teacher:
        raise HTTPException(status_code=400, detail="User is not a teacher.")

    existing = await db.execute(
        select(SchoolTeacher).where(
            SchoolTeacher.school_id == current_user.id,
            SchoolTeacher.teacher_id == teacher_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Teacher already in school.")

    school_teacher = SchoolTeacher(
        school_id=current_user.id,
        teacher_id=teacher_id
    )
    db.add(school_teacher)
    await db.commit()
    return {"message": "Teacher added successfully."}


@router.delete("/teachers/{teacher_id}")
async def remove_teacher(
    teacher_id: int,
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Школа убирает учителя"""
    relation = await db.execute(
        select(SchoolTeacher).where(
            SchoolTeacher.school_id == current_user.id,
            SchoolTeacher.teacher_id == teacher_id
        )
    )
    relation = relation.scalar_one_or_none()
    if not relation:
        raise HTTPException(status_code=404, detail="Teacher not found in school.")

    await db.delete(relation)
    await db.commit()
    return {"message": "Teacher removed successfully."}


@router.get("/my-teachers", response_model=list[UserBaseInfo])
async def my_teachers(
    current_user: User = Depends(role_required("school")),
    db: AsyncSession = Depends(get_db)
):
    """Мои учителя"""
    result = await db.execute(
        select(User)
        .join(SchoolTeacher, SchoolTeacher.teacher_id == User.id)
        .where(SchoolTeacher.school_id == current_user.id)
    )
    return result.scalars().all()

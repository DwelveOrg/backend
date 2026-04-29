from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.db_ext import get_db
from db.models.user import User, UserRole
from db.models.study_group import StudyGroup
from db.models.membership import GroupMembership
from app.schemas import UserBaseInfo
from app.dependencies.auth_deps import get_current_user, role_required

router = APIRouter(prefix="/school", tags=["school"])


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
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from db.db_ext import get_db
from db.models.user import User, UserRole
from db.models.study_group import StudyGroup, GroupType
from db.models.membership import GroupMembership
from app.schemas import GroupCreate, GroupListResponse, MsgResponse
from app.dependencies.auth_deps import get_current_user
from app.core.logger import log_security_event

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", response_model=GroupListResponse)
async def list_groups(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=50),
        subject: str | None = Query(None),
        group_type: GroupType | None = Query(None),
        current_user: User = Depends(get_current_user),  # теперь нужна авторизация
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    # Базовый запрос
    base_stmt = select(StudyGroup).where(StudyGroup.is_private == False)

    # Фильтры
    if subject:
        base_stmt = base_stmt.where(StudyGroup.subject.ilike(f"%{subject}%"))
    if group_type:
        base_stmt = base_stmt.where(StudyGroup.group_type == group_type)

    # Считаем total
    total_stmt = select(func.count()).select_from(
        base_stmt.subquery()
    )
    total = (await db.execute(total_stmt)).scalar() or 0

    # Получаем группы
    stmt = base_stmt.order_by(desc(StudyGroup.created_at)).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    groups = result.scalars().all()

    pages = (total + per_page - 1) // per_page

    return {
        "groups": groups,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }
    }


@router.get("/{group_id}")
async def get_group(
        group_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Просмотр одной группы"""
    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")
    return {
        "id": group.id,
        "name": group.name,
        "subject": group.subject,
        "tutor_name": group.tutor_name,
        "description": group.description,
        "capacity": group.capacity,
        "group_type": group.group_type,
        "is_private": group.is_private,
        "owner_id": group.owner_id,
        "created_at": group.created_at,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_group(
        payload: GroupCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Учитель или школа создаёт группу"""
    if not current_user.can_create_groups:
        log_security_event("UNAUTHORIZED_GROUP_CREATE", f"user_id={current_user.id}")
        raise HTTPException(status_code=403, detail="Only teachers and schools can create groups.")

    new_group = StudyGroup(
        **payload.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)
    return {"message": "Study group created successfully.", "id": new_group.id}


@router.post("/{group_id}/join", status_code=status.HTTP_201_CREATED)
async def join_group(
        group_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Вступить в группу"""
    if current_user.role not in (UserRole.student, UserRole.teacher):
        raise HTTPException(status_code=403, detail="Only students and teachers can join groups.")

    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    existing = (await db.execute(
        select(GroupMembership).where(
            GroupMembership.user_id == current_user.id,
            GroupMembership.group_id == group_id
        )
    )).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=409, detail="You already joined this group.")

    members_now = (await db.execute(
        select(func.count()).select_from(GroupMembership).where(
            GroupMembership.group_id == group_id
        )
    )).scalar() or 0

    if members_now >= group.capacity:
        raise HTTPException(status_code=409, detail="This group has reached full capacity.")

    membership = GroupMembership(user_id=current_user.id, group_id=group_id)
    db.add(membership)
    await db.commit()
    return {"message": "You successfully joined the study group."}


@router.delete("/{group_id}/leave", response_model=MsgResponse)
async def leave_group(
        group_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Выйти из группы"""
    membership = (await db.execute(
        select(GroupMembership).where(
            GroupMembership.user_id == current_user.id,
            GroupMembership.group_id == group_id
        )
    )).scalar_one_or_none()

    if not membership:
        raise HTTPException(status_code=404, detail="You are not a member of this group.")

    await db.delete(membership)
    await db.commit()
    return {"message": "You successfully left the group."}


@router.get("/{group_id}/members")
async def list_members(
        group_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Список участников группы"""
    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    result = await db.execute(
        select(User)
        .join(GroupMembership, GroupMembership.user_id == User.id)
        .where(GroupMembership.group_id == group_id)
    )
    members = result.scalars().all()
    return [
        {"id": m.id, "full_name": m.full_name, "role": m.role}
        for m in members
    ]


@router.delete("/{group_id}", response_model=MsgResponse)
async def delete_group(
        group_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Удалить группу — только владелец"""
    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found.")

    if group.owner_id != current_user.id and current_user.role != UserRole.school:
        raise HTTPException(status_code=403, detail="You are not the owner of this group.")

    await db.delete(group)
    await db.commit()
    return {"message": "Group deleted successfully."}
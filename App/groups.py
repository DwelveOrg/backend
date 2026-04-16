from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from DataBase.db_ext import get_db
from DataBase.models import User, StudyGroup, GroupMembership
from .schemas import GroupCreate, GroupListResponse, MsgResponse
from .auth_deps import get_current_user, role_required

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/membership/upgrade", response_model=MsgResponse)
async def upgrade_membership(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    # В FastAPI доступ к 'debug' обычно через настройки (Settings)
    # Но для примера оставим логику
    current_user.paid_member = True
    await db.commit()
    return {"message": "Membership upgraded successfully."}


@router.get("/", response_model=GroupListResponse)
async def list_groups(
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=50),
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    # Считаем общее количество
    total_stmt = select(func.count()).select_from(StudyGroup)
    total_res = await db.execute(total_stmt)
    total = total_res.scalar() or 0

    # Получаем элементы
    stmt = select(StudyGroup).order_by(desc(StudyGroup.created_at)).offset(offset).limit(per_page)
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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_group(
        payload: GroupCreate,
        current_user: User = Depends(role_required("teacher")),
        db: AsyncSession = Depends(get_db)
):
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
        current_user: User = Depends(role_required("student")),
        db: AsyncSession = Depends(get_db)
):
    # Проверяем существование группы
    group = await db.get(StudyGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Проверяем, не состоит ли уже
    existing_stmt = select(GroupMembership).where(
        GroupMembership.user_id == current_user.id,
        GroupMembership.group_id == group_id
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="You already joined this group.")

    # Считаем текущее кол-во участников
    count_stmt = select(func.count()).where(GroupMembership.group_id == group_id)
    members_now = (await db.execute(count_stmt)).scalar() or 0

    if members_now >= group.capacity:
        raise HTTPException(status_code=409, detail="This group has reached full capacity.")

    membership = GroupMembership(user_id=current_user.id, group_id=group_id)
    db.add(membership)
    await db.commit()
    return {"message": "You successfully joined the study group."}
import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.platform.database import get_db
from app.modules.disputes.models import Dispute, DisputeStatus
from app.modules.disputes.schemas import DisputeCreate, DisputeResolve, DisputeResponse
from app.modules.identity.dependencies import get_current_user
from app.modules.identity.models import User
from app.modules.workspaces.models import Workspace

router = APIRouter(prefix="/disputes", tags=["Disputes & Arbitration"])


async def get_user_workspace(user: User, db: AsyncSession) -> Workspace:
    res = await db.execute(select(Workspace).where(Workspace.owner_id == user.id))
    workspace = res.scalars().first()
    if not workspace:
        raise HTTPException(status_code=400, detail="Workspace not found for user")
    return workspace


@router.post("/", response_model=DisputeResponse, status_code=status.HTTP_201_CREATED)
async def create_dispute(
    payload: DisputeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Открыть спор по заказу"""
    workspace = await get_user_workspace(current_user, db)

    dispute = Dispute(
        order_id=payload.order_id,
        initiator_workspace_id=workspace.id,
        reason=payload.reason,
        description=payload.description,
        status=DisputeStatus.OPENED,
    )
    db.add(dispute)
    await db.commit()
    await db.refresh(dispute)
    return dispute


@router.get("/", response_model=List[DisputeResponse])
async def list_disputes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить список споров текущего воркспейса"""
    workspace = await get_user_workspace(current_user, db)
    result = await db.execute(
        select(Dispute).where(Dispute.initiator_workspace_id == workspace.id)
    )
    return result.scalars().all()


@router.patch("/{dispute_id}/resolve", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: uuid.UUID,
    payload: DisputeResolve,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Разрешить спор (арбитраж / модерация)"""
    res = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = res.scalars().first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    dispute.status = payload.status
    dispute.resolution_comment = payload.resolution_comment
    await db.commit()
    await db.refresh(dispute)
    return dispute

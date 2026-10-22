import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.platform.database import get_db
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationResponse

router = APIRouter(prefix="", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def list_my_notifications(
    workspace_id: uuid.UUID,  # Позже привяжем к current_user
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.workspace_id == workspace_id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


@router.post("/", response_model=NotificationResponse, status_code=201)
async def create_notification(
    workspace_id: uuid.UUID,
    title: str,
    message: str,
    db: AsyncSession = Depends(get_db),
):
    notification = Notification(
        workspace_id=workspace_id,
        title=title,
        message=message,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

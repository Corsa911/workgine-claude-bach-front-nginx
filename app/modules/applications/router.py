import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.platform.database import get_db
from app.modules.applications.models import Application, ApplicationStatus
from app.modules.applications.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
)

router = APIRouter(prefix="", tags=["Applications"])


@router.post(
    "/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
async def create_application(
    payload: ApplicationCreate, db: AsyncSession = Depends(get_db)
):
    application = Application(
        order_id=payload.order_id,
        freelancer_workspace_id=payload.freelancer_workspace_id,
        cover_letter=payload.cover_letter,
        bid_amount_minor=payload.bid_amount_minor,
        currency=payload.currency,
        status=ApplicationStatus.PENDING.value,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    applications = result.scalars().all()
    return applications


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
async def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = payload.status.value
    await db.commit()
    await db.refresh(application)
    return application

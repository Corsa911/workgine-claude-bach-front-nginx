import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.platform.database import get_db
from app.modules.reviews.models import Review
from app.modules.reviews.schemas import ReviewCreate, ReviewResponse
from app.modules.identity.dependencies import get_current_user
from app.modules.identity.models import User
from app.modules.workspaces.models import Workspace

router = APIRouter(prefix="", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Находим воркспейс текущего пользователя
    ws_result = await db.execute(
        select(Workspace).where(Workspace.owner_id == current_user.id)
    )
    workspace = ws_result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no active workspace",
        )

    review = Review(
        order_id=payload.order_id,
        author_workspace_id=workspace.id,  # Берем автоматически из токена!
        target_workspace_id=payload.target_workspace_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@router.get("/workspace/{workspace_id}", response_model=List[ReviewResponse])
async def list_workspace_reviews(
    workspace_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Review).where(Review.target_workspace_id == workspace_id)
    )
    reviews = result.scalars().all()
    return reviews

import uuid
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.platform.database import get_db
from app.modules.identity.dependencies import get_current_workspace
from app.modules.workspaces.models import Workspace
from app.modules.marketplace.models import Order
from app.modules.marketplace.schemas import (
    OrderCreate,
    OrderUpdate,
    OrderPublish,
    OrderResponse,
)
from app.modules.marketplace.service import editable_order, category_exists

router = APIRouter()


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    ws: Workspace = Depends(get_current_workspace),
):
    await category_exists(db, payload.category_id)
    order = Order(
        **payload.model_dump(),
        customer_workspace_id=ws.id,
        status="draft",
        visibility="public",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    scope: Literal["mine", "market"] = "market",
    status_filter: Literal["draft", "published"] | None = None,
    q: str = Query(default="", max_length=200),
    category_id: uuid.UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    ws: Workspace = Depends(get_current_workspace),
):
    query = select(Order)
    if scope == "mine":
        query = query.where(Order.customer_workspace_id == ws.id)
        if status_filter:
            query = query.where(Order.status == status_filter)
    else:
        query = query.where(
            Order.status == "published",
            Order.visibility == "public",
            Order.customer_workspace_id != ws.id,
        )
    if q.strip():
        query = query.where(Order.title.icontains(q.strip(), autoescape=True))
    if category_id:
        query = query.where(Order.category_id == category_id)
    return (
        await db.scalars(
            query.order_by(Order.created_at.desc(), Order.id)
            .limit(limit)
            .offset(offset)
        )
    ).all()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ws: Workspace = Depends(get_current_workspace),
):
    order = await db.get(Order, order_id)
    if not order or (
        order.customer_workspace_id != ws.id
        and not (order.status == "published" and order.visibility == "public")
    ):
        raise HTTPException(404, "Заказ не найден")
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: uuid.UUID,
    payload: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    ws: Workspace = Depends(get_current_workspace),
):
    order = await editable_order(db, order_id, ws.id, payload.version)
    await category_exists(db, payload.category_id)
    for key, value in payload.model_dump(exclude={"version"}).items():
        setattr(order, key, value)
    order.version += 1
    await db.commit()
    await db.refresh(order)
    return order


@router.post("/{order_id}/publish", response_model=OrderResponse)
async def publish_order(
    order_id: uuid.UUID,
    payload: OrderPublish,
    db: AsyncSession = Depends(get_db),
    ws: Workspace = Depends(get_current_workspace),
):
    order = await editable_order(db, order_id, ws.id, payload.version)
    if (
        not order.category_id
        or order.budget_minor <= 0
        or len(order.description.strip()) < 20
    ):
        raise HTTPException(
            422,
            "Для публикации выберите категорию, укажите бюджет и описание от 20 символов",
        )
    await category_exists(db, order.category_id)
    order.status = "published"
    order.version += 1
    await db.commit()
    await db.refresh(order)
    return order

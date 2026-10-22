import uuid
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.marketplace.models import Order
from app.modules.catalog.models import Category


async def category_exists(db: AsyncSession, category_id: uuid.UUID | None):
    if category_id is not None:
        category = await db.get(Category, category_id)
        if not category or not category.is_active:
            raise HTTPException(422, "Выберите доступную категорию")


async def editable_order(
    db: AsyncSession, order_id: uuid.UUID, workspace_id: uuid.UUID, version: int
):
    order = await db.scalar(select(Order).where(Order.id == order_id).with_for_update())
    if not order or order.customer_workspace_id != workspace_id:
        raise HTTPException(404, "Заказ не найден")
    if order.status != "draft":
        raise HTTPException(409, "Редактировать можно только черновик")
    if order.version != version:
        raise HTTPException(409, "Заказ уже изменен. Обновите страницу")
    return order

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.platform.database import get_db
from app.modules.catalog.models import Category
from app.modules.catalog.schemas import CategoryResponse

router = APIRouter()


@router.get("/categories", response_model=list[CategoryResponse])
async def categories(db: AsyncSession = Depends(get_db)):
    return (
        await db.scalars(
            select(Category).where(Category.is_active.is_(True)).order_by(Category.name)
        )
    ).all()

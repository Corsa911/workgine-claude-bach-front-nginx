import asyncio
import uuid
from sqlalchemy import select
from app.platform.database import async_session_maker, engine
from app.modules.catalog.models import Category
from app.platform import models  # noqa: F401

CATEGORIES = [
    ("design", "Дизайн"),
    ("development", "Разработка"),
    ("marketing", "Маркетинг"),
    ("texts", "Тексты и переводы"),
    ("video", "Фото и видео"),
    ("business", "Бизнес и консультации"),
]


async def seed():
    async with async_session_maker() as db:
        for slug, name in CATEGORIES:
            if not await db.scalar(select(Category).where(Category.slug == slug)):
                db.add(
                    Category(
                        id=uuid.uuid5(uuid.NAMESPACE_URL, "workgine/category/" + slug),
                        slug=slug,
                        name=name,
                    )
                )
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

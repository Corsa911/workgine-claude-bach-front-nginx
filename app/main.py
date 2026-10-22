from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.platform.config import settings
from app.platform.database import engine
from app.platform import models  # noqa: F401
from app.modules.identity.router import router as auth
from app.modules.marketplace.router import router as orders
from app.modules.profiles.router import router as profiles
from app.modules.catalog.router import router as catalog


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Workgine API",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    openapi_url="/openapi.json" if settings.DOCS_ENABLED else None,
)
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_methods=["GET", "POST", "PUT", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )
app.include_router(auth, prefix="/api/v1/auth", tags=["Account"])
app.include_router(orders, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(profiles, prefix="/api/v1/profiles", tags=["Profile"])
app.include_router(catalog, prefix="/api/v1/catalog", tags=["Catalog"])
# Legacy applications/payments/chat/reviews/disputes/notifications are deliberately
# not mounted until their authorization and transaction rules are implemented.


@app.get("/health")
async def health():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ok"}

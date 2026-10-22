import os
import pytest_asyncio
from sqlalchemy import event, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport

TEST_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["DATABASE_URL"] = TEST_URL
os.environ["SECRET_KEY"] = "isolated-test-secret-which-is-at-least-32-chars"
from app.main import app
from app.platform.database import Base, get_db


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(TEST_URL)
    if TEST_URL.startswith("sqlite"):

        @event.listens_for(engine.sync_engine, "connect")
        def foreign_keys(conn, record):
            conn.execute("PRAGMA foreign_keys=ON")

    # Apply actual migrations to a fresh schema; never point TEST_DATABASE_URL at real data.
    async with engine.begin() as conn:

        def migrate(sync_conn):
            from alembic.migration import MigrationContext
            from alembic.operations import Operations
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "baseline", "alembic/versions/0001_initial.py"
            )
            baseline = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(baseline)
            with Operations.context(MigrationContext.configure(sync_conn)):
                baseline.upgrade()

        await conn.run_sync(migrate)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    async def override():
        async with sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        if not TEST_URL.startswith("sqlite"):
            from sqlalchemy import text

            for name in ["transactiontype", "transactionstatus", "disputestatus"]:
                await conn.execute(text(f"DROP TYPE IF EXISTS {name}"))
    await engine.dispose()

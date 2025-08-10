from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.api.dependencies import get_db
from app.core.config import settings
from app.enums import Genders, PreferredGenders, UILanguages
from app.models import base
from app.schemas.preferences import PreferencesInSchema
from bot.schemas.user import UserInSchema
from main import app


@pytest_asyncio.fixture(name="engine", scope="session")
async def create_db_engine() -> AsyncGenerator[AsyncEngine]:
    """Create a test database engine."""
    test_db_name = f"test_{settings.POSTGRES_DB}"
    test_db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{test_db_name}"

    admin_engine = create_async_engine(
        settings.database_url,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    async with admin_engine.begin() as conn:
        await conn.execute(text(f"CREATE DATABASE {test_db_name}"))

    test_engine = create_async_engine(
        test_db_url,
        poolclass=NullPool,
    )
    async with test_engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)

    yield test_engine
    await test_engine.dispose()

    async with admin_engine.connect() as conn:
        await conn.execute(
            text(
                f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{test_db_name}'
              AND pid <> pg_backend_pid();
        """,  # noqa: S608
            ),
        )
        await conn.execute(text(f"DROP DATABASE {test_db_name}"))

    await admin_engine.dispose()


@pytest_asyncio.fixture(name="session")
async def session_fixture(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Create a test session with a mocked database engine."""
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
        await session.close()
        await transaction.rollback()


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Create a test client with a mocked database session."""

    def get_db_override() -> AsyncSession:
        """Return the mocked database session."""
        return session

    app.dependency_overrides[get_db] = get_db_override

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def get_test_user() -> UserInSchema:
    """Create a test user."""
    return UserInSchema(
        telegram_id=3123421231,
        name="Test User",
        birth_date=datetime(2004, 11, 19, tzinfo=UTC),
        bio="Test bio",
        gender=Genders.female,
        latitude=55.755826,
        longitude=37.6173,
        ui_language=UILanguages.en,
        is_location_precise=True,
    )


@pytest.fixture(name="test_preferences")
def get_test_preferences() -> PreferencesInSchema:
    """Create a test preferences."""
    return PreferencesInSchema(
        min_age=18,
        max_age=25,
        preferred_gender=PreferredGenders.male,
    )

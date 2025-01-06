from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=True)


async def get_version():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT version()"))
        return res.first()

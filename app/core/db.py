from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

session_factory = async_sessionmaker(engine)

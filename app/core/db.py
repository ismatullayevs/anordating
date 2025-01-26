from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings


engine = create_async_engine(settings.database_url, echo=settings.DEBUG)

session_factory = async_sessionmaker(engine, expire_on_commit=False)

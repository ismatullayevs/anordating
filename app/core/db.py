from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

session_factory = async_sessionmaker(engine)


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        """Pretty print the model instance."""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

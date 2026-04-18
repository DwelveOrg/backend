from typing import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.base import Base

# Берём URL из переменной окружения — легко менять в Docker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./project.db")

# echo=True только в режиме разработки
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

engine = create_async_engine(DATABASE_URL, echo=DEBUG)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Создаёт все таблицы при старте приложения."""
    # Импортируем все модели чтобы SQLAlchemy их увидел
    import db.models.user       # noqa: F401
    import db.models.study_group  # noqa: F401
    import db.models.membership   # noqa: F401
    import db.models.submission   # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
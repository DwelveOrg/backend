from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# URL базы данных. Для примера используем SQLite (асинхронный драйвер aiosqlite)
# Если используешь PostgreSQL: postgresql+asyncpg://user:pass@localhost/dbname
DATABASE_URL = "sqlite+aiosqlite:///./project.db"

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Базовый класс для моделей (мы его уже использовали в предыдущих файлах)
class Base(DeclarativeBase):
    pass

# Зависимость для эндпоинтов (Dependency Injection)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
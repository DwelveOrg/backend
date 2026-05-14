import os
os.environ["TESTING"] = "true"

from unittest.mock import patch, AsyncMock
# Мокаем slowapi ДО импорта приложения
import slowapi.extension
original_check = slowapi.extension.Limiter._check_request_limit

async def mock_check(*args, **kwargs):
    pass

slowapi.extension.Limiter._check_request_limit = mock_check

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db.base import Base
from db.db_ext import get_db
from main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL)
test_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    import db.models.user
    import db.models.study_group
    import db.models.membership
    import db.models.submission
    import db.models.assignment
    import db.models.grade
    import db.models.school      # ← добавь!
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def redis_store():
    store = {}

    async def fake_setex(key, ttl, value):
        store[key] = value

    async def fake_get(key):
        return store.get(key)

    async def fake_delete(key):
        store.pop(key, None)

    with patch("app.core.redis.redis_client") as mock:
        mock.setex = fake_setex
        mock.get = fake_get
        mock.delete = fake_delete
        yield store


@pytest_asyncio.fixture
async def client(redis_store):
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
import os
import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from db.base import Base
import db.models.user        # noqa
import db.models.study_group # noqa
import db.models.membership  # noqa
    import db.models.submission  # noqa
    import db.models.user        # noqa
import db.models.study_group # noqa
import db.models.membership  # noqa
import db.models.submission  # noqa
import db.models.assignment  # noqa
import db.models.grade       # noqa
import db.models.assignment  # noqa
import db.models.school      # noqa

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./project.db")

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True  # Важно для SQLite!
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from src.core.database import Base
from src.auth.models import User, UserSession
from src.rooms.models import Room, RoomMember, JoinLink
from src.chat.models import Message, Attachment, PinnedMessage
from src.moderation.models import Ban
from src.core.settings import settings

config = context.config

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")
logger.info(f"Using DATABASE_URL: {settings.DATABASE_URL}")
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
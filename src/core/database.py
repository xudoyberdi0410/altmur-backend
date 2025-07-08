from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.settings import settings

class Base(DeclarativeBase):
    """Base class for all models."""
    pass

def get_async_engine():
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30
    )

def get_async_session_maker():
    engine = get_async_engine()
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_db():
    AsyncSessionLocal = get_async_session_maker()
    async with AsyncSessionLocal() as session:
        yield session
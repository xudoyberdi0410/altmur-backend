import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.auth import repository
from src.auth.models import User, UserSession
from src.core.database import Base
import asyncio


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_and_get_user(async_session):
    user = User(username="testuser", first_name="Test", family_name="User", email="test@example.com", hashed_password="hashed", is_admin=False)
    created = await repository.create_user(async_session, user)
    assert created.user_id is not None
    fetched = await repository.get_user_by_id(async_session, created.user_id)
    assert fetched.username == "testuser"
    fetched_by_email = await repository.get_user_by_email(async_session, "test@example.com")
    assert fetched_by_email.user_id == created.user_id
    fetched_by_username = await repository.get_user_by_username(async_session, "testuser")
    assert fetched_by_username.user_id == created.user_id

@pytest.mark.asyncio
async def test_update_user(async_session):
    user = User(username="updateuser", first_name="Update", family_name="User", email="update@example.com", hashed_password="hashed", is_admin=False)
    await repository.create_user(async_session, user)
    updated = await repository.update_user_by_id(async_session, user.user_id, {"first_name": "Updated"})
    assert updated.first_name == "Updated"

@pytest.mark.asyncio
async def test_delete_user(async_session):
    user = User(username="deleteuser", first_name="Delete", family_name="User", email="delete@example.com", hashed_password="hashed", is_admin=False)
    await repository.create_user(async_session, user)
    await repository.delete_user(async_session, user)
    fetched = await repository.get_user_by_id(async_session, user.user_id)
    assert fetched is None

@pytest.mark.asyncio
async def test_create_and_get_user_session(async_session):
    user = User(username="sessuser", first_name="Sess", family_name="User", email="sess@example.com", hashed_password="hashed", is_admin=False)
    await repository.create_user(async_session, user)
    session = UserSession(user_id=user.user_id, refresh_token="token123", user_agent="agent", ip_address="127.0.0.1", is_active=True)
    created = await repository.create_user_session(async_session, session)
    assert created.session_id is not None
    fetched = await repository.get_user_session_by_id(async_session, created.session_id)
    assert fetched.refresh_token == "token123"
    fetched_by_token = await repository.get_user_session_by_refresh_token(async_session, "token123")
    assert fetched_by_token.session_id == created.session_id

@pytest.mark.asyncio
async def test_update_user_session(async_session):
    user = User(username="sessupdate", first_name="Sess", family_name="Update", email="sessupdate@example.com", hashed_password="hashed", is_admin=False)
    await repository.create_user(async_session, user)
    session = UserSession(user_id=user.user_id, refresh_token="token456", user_agent="agent", ip_address="127.0.0.1", is_active=True)
    await repository.create_user_session(async_session, session)
    updated = await repository.update_user_session_by_id(async_session, session.session_id, {"is_active": False})
    assert updated.is_active is False

@pytest.mark.asyncio
async def test_delete_user_session(async_session):
    user = User(username="sessdelete", first_name="Sess", family_name="Delete", email="sessdelete@example.com", hashed_password="hashed", is_admin=False)
    await repository.create_user(async_session, user)
    session = UserSession(user_id=user.user_id, refresh_token="token789", user_agent="agent", ip_address="127.0.0.1", is_active=True)
    await repository.create_user_session(async_session, session)
    await repository.delete_user_session(async_session, session)
    fetched = await repository.get_user_session_by_id(async_session, session.session_id)
    assert fetched is None

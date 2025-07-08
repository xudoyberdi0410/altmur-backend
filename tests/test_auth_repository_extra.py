import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
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

@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
    return engine

@pytest.fixture(scope="session", autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def async_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()  # ensure clean state

@pytest.mark.asyncio
async def test_create_user_unique_constraints(async_session):
    user1 = User(username="uniqueuser", first_name="A", family_name="B", email="unique@example.com", hashed_password="h", is_admin=False)
    await repository.create_user(async_session, user1)
    user2 = User(username="uniqueuser", first_name="C", family_name="D", email="other@example.com", hashed_password="h", is_admin=False)
    with pytest.raises(IntegrityError):
        await repository.create_user(async_session, user2)
    user3 = User(username="otheruser", first_name="E", family_name="F", email="unique@example.com", hashed_password="h", is_admin=False)
    with pytest.raises(IntegrityError):
        await repository.create_user(async_session, user3)

@pytest.mark.asyncio
async def test_get_nonexistent_user(async_session):
    user = await repository.get_user_by_id(async_session, 9999)
    assert user is None
    user = await repository.get_user_by_email(async_session, "nope@example.com")
    assert user is None
    user = await repository.get_user_by_username(async_session, "nope")
    assert user is None

@pytest.mark.asyncio
async def test_update_nonexistent_user(async_session):
    updated = await repository.update_user_by_id(async_session, 9999, {"first_name": "X"})
    assert updated is None

@pytest.mark.asyncio
async def test_create_user_session_for_nonexistent_user(async_session):
    session = UserSession(user_id=9999, refresh_token="badtoken", user_agent="ua", ip_address="127.0.0.1", is_active=True)
    with pytest.raises(IntegrityError):
        await repository.create_user_session(async_session, session)

@pytest.mark.asyncio
async def test_update_nonexistent_user_session(async_session):
    updated = await repository.update_user_session_by_id(async_session, 9999, {"is_active": False})
    assert updated is None

@pytest.mark.asyncio
async def test_get_nonexistent_user_session(async_session):
    session = await repository.get_user_session_by_id(async_session, 9999)
    assert session is None
    session = await repository.get_user_session_by_refresh_token(async_session, "notoken")
    assert session is None

@pytest.mark.asyncio
@pytest.mark.parametrize("is_admin", [True, False])
async def test_create_user_parametrize(async_session, is_admin):
    user = User(username=f"paramuser{is_admin}", first_name="F", family_name="L", email=f"param{is_admin}@ex.com", hashed_password="h", is_admin=is_admin)
    created = await repository.create_user(async_session, user)
    fetched = await repository.get_user_by_id(async_session, created.user_id)
    assert fetched.is_admin == is_admin
    assert fetched.first_name == "F"
    assert fetched.family_name == "L"
    assert fetched.email == f"param{is_admin}@ex.com"
    assert fetched.hashed_password == "h"

@pytest.mark.asyncio
async def test_transaction_rollback_on_error(async_session):
    user = User(username="rollbackuser", first_name="A", family_name="B", email="rollback@example.com", hashed_password="h", is_admin=False)
    await repository.create_user(async_session, user)
    # Try to create another user with same username (should fail)
    user2 = User(username="rollbackuser", first_name="C", family_name="D", email="rollback2@example.com", hashed_password="h", is_admin=False)
    with pytest.raises(IntegrityError):
        await repository.create_user(async_session, user2)
    # The second user should not be in DB
    users = await repository.get_all_users(async_session)
    assert len([u for u in users if u.username == "rollbackuser"]) == 1

@pytest.mark.asyncio
async def test_create_user_session_fields(async_session):
    user = User(username="sessionfields", first_name="A", family_name="B", email="sessionfields@example.com", hashed_password="h", is_admin=False)
    await repository.create_user(async_session, user)
    session = UserSession(user_id=user.user_id, refresh_token="fieldtoken", user_agent="testagent", ip_address="8.8.8.8", is_active=True)
    created = await repository.create_user_session(async_session, session)
    fetched = await repository.get_user_session_by_id(async_session, created.session_id)
    assert fetched.user_id == user.user_id
    assert fetched.refresh_token == "fieldtoken"
    assert fetched.user_agent == "testagent"
    assert fetched.ip_address == "8.8.8.8"
    assert fetched.is_active is True
    assert fetched.created_at is not None
    assert fetched.expired_at is None

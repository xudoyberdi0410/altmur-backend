import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.auth import repository
from src.models import User, UserSession, RoomMember, JoinLink, Message, Ban
from src.core.database import Base
import asyncio

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine(DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async_session = async_sessionmaker(bind=conn, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session

@pytest.mark.asyncio
async def test_user_repository_full(test_session):
    user_repo = repository.UserRepository(test_session)

    # 1. Create user
    user = await user_repo.create(
        username="testuser",
        first_name="Test",
        family_name="User",
        email="blabla@gmail.com",
        hashed_password="hashedpassword"
    )
    assert user.user_id is not None

    # 2. Get by ID
    fetched = await user_repo.get_by_id(user.user_id)
    assert fetched is not None
    assert fetched.username == "testuser"

    # 3. Get by email
    fetched_by_email = await user_repo.get_by_email("blabla@gmail.com")
    assert fetched_by_email.user_id == user.user_id

    # 4. Get by username
    fetched_by_username = await user_repo.get_by_username("testuser")
    assert fetched_by_username.user_id == user.user_id

    # 5. Exists
    exists = await user_repo.exists(user.user_id)
    assert exists is True

    # 6. Count
    count = await user_repo.count()
    assert count == 1

    # 7. Update
    updated = await user_repo.update(user.user_id, first_name="Updated", family_name="Name")
    assert updated is not None
    assert updated.first_name == "Updated"

    # 8. Delete
    deleted = await user_repo.delete(user.user_id)
    assert deleted is True

    # 9. Not exists anymore
    exists_after_delete = await user_repo.exists(user.user_id)
    assert exists_after_delete is False

@pytest.mark.asyncio
async def test_user_session_repository(test_session):
    user_repo = repository.UserRepository(test_session)
    session_repo = repository.UserSessionRepository(test_session)

    # Создаём пользователя
    user = await user_repo.create(
        username="anotheruser",
        first_name="Another",
        family_name="User",
        email="another@gmail.com",
        hashed_password="hashed"
    )

    # Создаём сессию
    user_session = await session_repo.create(
        user_id=user.user_id,
        user_agent="TestAgent",
        refresh_token="REFRESH123"
    )

    # Получаем по refresh_token
    session_by_token = await session_repo.get_by_refresh_token("REFRESH123")
    assert session_by_token is not None
    assert session_by_token.user_id == user.user_id

    # Получаем по user_id
    sessions = await session_repo.get_by_user_id(user.user_id)
    assert len(sessions) == 1
    assert sessions[0].refresh_token == "REFRESH123"

    # Удаление
    deleted = await session_repo.delete(user_session.session_id)
    assert deleted is True

    # Проверка удаления
    session_after_delete = await session_repo.get_by_id(user_session.session_id)
    assert session_after_delete is None

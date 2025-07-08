from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import User, UserSession

# Getters for User and UserSession models
async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Fetch a user by their ID."""
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Fetch a user by their email address."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Fetch a user by their username."""
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def get_all_users(session: AsyncSession) -> list[User]:
    """Fetch all users."""
    result = await session.execute(select(User))
    return result.scalars().all()

async def get_user_session_by_id(session: AsyncSession, session_id: int) -> UserSession | None:
    """Fetch a user session by its ID."""
    result = await session.execute(select(UserSession).where(UserSession.session_id == session_id))
    return result.scalar_one_or_none()

async def get_user_session_by_refresh_token(session: AsyncSession, refresh_token: str) -> UserSession | None:
    """Fetch a user session by its refresh token."""
    result = await session.execute(select(UserSession).where(UserSession.refresh_token == refresh_token))
    return result.scalar_one_or_none()

async def get_user_sessions_by_user_id(session: AsyncSession, user_id: int) -> list[UserSession]:
    """Fetch all user sessions for a specific user."""
    result = await session.execute(select(UserSession).where(UserSession.user_id == user_id))
    return result.scalars().all()

async def get_all_user_sessions(session: AsyncSession) -> list[UserSession]:
    """Fetch all user sessions."""
    result = await session.execute(select(UserSession))
    return result.scalars().all()

# Create functions for User and UserSession models
async def create_user(session: AsyncSession, user: User) -> User:
    """Create a new user."""
    async with session.begin():
        session.add(user)
        await session.refresh(user)
        return user

async def create_user_session(session: AsyncSession, user_session: UserSession) -> UserSession:
    """Create a new user session."""
    async with session.begin():
        session.add(user_session)
        await session.refresh(user_session)
        return user_session

# Update functions for User and UserSession models
async def update_user_by_id(session: AsyncSession, user_id: int, user_data: dict) -> User | None:
    """Update an existing user by their ID."""
    async with session.begin():
        user = await get_user_by_id(session, user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            await session.refresh(user)
            return user
        return None

async def update_user_session_by_id(session: AsyncSession, session_id: int, session_data: dict) -> UserSession | None:
    """Update an existing user session by its ID."""
    async with session.begin():
        user_session = await get_user_session_by_id(session, session_id)
        if user_session:
            for key, value in session_data.items():
                setattr(user_session, key, value)
            await session.refresh(user_session)
            return user_session
        return None


# Delete functions for User and UserSession models
async def delete_user(session: AsyncSession, user: User) -> None:
    """Delete a user."""
    async with session.begin():
        await session.delete(user)

async def delete_user_session(session: AsyncSession, user_session: UserSession) -> None:
    """Delete a user session."""
    async with session.begin():
        await session.delete(user_session)



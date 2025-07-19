from src.core.repository import BaseRepository

from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, UserSession


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
       
    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address."""
        return await super().get_by_field('email', email)
        
    async def get_by_username(self, username: str) -> User | None:
        """Fetch a user by their username."""
        return await super().get_by_field('username', username)

class UserSessionRepository(BaseRepository[UserSession]):
    """Repository for UserSession model operations."""
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserSession)
        
    async def get_by_refresh_token(self, refresh_token: str) -> UserSession | None:
        """Fetch a user session by its refresh token."""
        return await super().get_by_field('refresh_token', refresh_token)
    
    async def get_by_user_id(self, user_id: int) -> list[UserSession]:
        """Fetch all user sessions for a specific user."""
        return await super().get_by_fields(user_id=user_id)    
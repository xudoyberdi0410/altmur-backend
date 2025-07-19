import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

# Импорт ваших классов
try:
    from src.auth.repository import UserRepository, UserSessionRepository
    from src.auth.models import User, UserSession
except ImportError:
    # Заглушки для тестирования
    class User:
        def __init__(self, user_id=None, username=None, first_name=None, 
                     family_name=None, email=None, hashed_password=None):
            self.user_id = user_id
            self.username = username
            self.first_name = first_name
            self.family_name = family_name
            self.email = email
            self.hashed_password = hashed_password
    
    class UserSession:
        def __init__(self, session_id=None, user_id=None, refresh_token=None, user_agent=None):
            self.session_id = session_id
            self.user_id = user_id
            self.refresh_token = refresh_token
            self.user_agent = user_agent
    
    class UserRepository:
        def __init__(self, session):
            self.session = session
    
    class UserSessionRepository:
        def __init__(self, session):
            self.session = session


class TestUserRepository:
    """Unit tests for UserRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock AsyncSession for unit tests"""
        session = AsyncMock(spec=AsyncSession)
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def user_repo(self, mock_session):
        """UserRepository instance with mocked session"""
        return UserRepository(mock_session)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repo, mock_session):
        """Test successful user creation"""
        # Arrange
        mock_user = User(
            user_id=1,
            username="testuser",
            first_name="Test",
            family_name="User",
            email="test@example.com",
            hashed_password="hashed123"
        )
        
        # Mock refresh to simulate setting user_id after commit
        async def mock_refresh(user):
            user.user_id = 1
        
        mock_session.refresh.side_effect = mock_refresh
        
        # Act
        result = await user_repo.create(
            username="testuser",
            first_name="Test",
            family_name="User",
            email="test@example.com",
            hashed_password="hashed123"
        )
        
        # Assert
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_database_error(self, user_repo, mock_session):
        """Test user creation with database error"""
        # Arrange
        mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repo.create(
                username="testuser",
                first_name="Test",
                family_name="User", 
                email="test@example.com",
                hashed_password="hashed123"
            )
        
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, user_repo, mock_session):
        """Test getting user by ID when user exists"""
        # Arrange
        mock_user = User(user_id=1, username="testuser", email="test@example.com")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_by_id(1)
        
        # Assert
        assert result == mock_user
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, user_repo, mock_session):
        """Test getting user by ID when user doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_by_id(999)
        
        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_email_found(self, user_repo, mock_session):
        """Test getting user by email when user exists"""
        # Arrange
        mock_user = User(user_id=1, username="testuser", email="test@example.com")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_by_email("test@example.com")
        
        # Assert
        assert result == mock_user
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, user_repo, mock_session):
        """Test getting user by email when user doesn't exist"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_by_email("nonexistent@example.com")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_username_found(self, user_repo, mock_session):
        """Test getting user by username when user exists"""
        # Arrange
        mock_user = User(user_id=1, username="testuser", email="test@example.com")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_by_username("testuser")
        
        # Assert
        assert result == mock_user
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repo, mock_session):
        """Test successful user update"""
        # Arrange
        mock_user = User(
            user_id=1,
            username="testuser",
            first_name="Updated",
            family_name="Name",
            email="test@example.com"
        )
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.update(1, first_name="Updated", family_name="Name")
        
        # Assert
        assert result == mock_user
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repo, mock_session):
        """Test updating non-existent user"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.update(999, first_name="New")
        
        # Assert
        assert result is None
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_repo, mock_session):
        """Test successful user deletion"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.delete(1)
        
        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_repo, mock_session):
        """Test deleting non-existent user"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.delete(999)
        
        # Assert
        assert result is False
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exists_user_found(self, user_repo, mock_session):
        """Test checking existence of existing user"""
        # Arrange
        mock_user = User(user_id=1)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.exists(1)
        
        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exists_user_not_found(self, user_repo, mock_session):
        """Test checking existence of non-existent user"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.exists(999)
        
        # Assert
        assert result is False
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_users(self, user_repo, mock_session):
        """Test counting users"""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.count()
        
        # Assert
        assert result == 5
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_users(self, user_repo, mock_session):
        """Test getting all users"""
        # Arrange
        mock_users = [
            User(user_id=1, username="user1"),
            User(user_id=2, username="user2")
        ]
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = mock_users
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await user_repo.get_all()
        
        # Assert
        assert len(result) == 2
        assert result[0].username == "user1"
        assert result[1].username == "user2"
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, user_repo, mock_session):
        """Test that database errors are properly raised"""
        # Arrange
        mock_session.execute.side_effect = SQLAlchemyError("Database connection failed")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repo.get_by_id(1)


class TestUserSessionRepository:
    """Unit tests for UserSessionRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock AsyncSession for unit tests"""
        session = AsyncMock(spec=AsyncSession)
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def session_repo(self, mock_session):
        """UserSessionRepository instance with mocked session"""
        return UserSessionRepository(mock_session)
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, session_repo, mock_session):
        """Test successful session creation"""
        # Arrange
        async def mock_refresh(session):
            session.session_id = 1
        
        mock_session.refresh.side_effect = mock_refresh
        
        # Act
        result = await session_repo.create(
            user_id=1,
            refresh_token="token123",
            user_agent="TestAgent"
        )
        
        # Assert
        assert result.user_id == 1
        assert result.refresh_token == "token123"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_refresh_token_found(self, session_repo, mock_session):
        """Test getting session by refresh token when exists"""
        # Arrange
        mock_session_obj = UserSession(session_id=1, user_id=1, refresh_token="token123")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_session_obj
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await session_repo.get_by_refresh_token("token123")
        
        # Assert
        assert result == mock_session_obj
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_user_id(self, session_repo, mock_session):
        """Test getting sessions by user ID"""
        # Arrange
        mock_sessions = [
            UserSession(session_id=1, user_id=1, refresh_token="token1"),
            UserSession(session_id=2, user_id=1, refresh_token="token2")
        ]
        mock_result = AsyncMock()
        mock_scalars = AsyncMock()
        mock_scalars.all.return_value = mock_sessions
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        # Act
        result = await session_repo.get_by_user_id(1)
        
        # Assert
        assert len(result) == 2
        assert result[0].refresh_token == "token1"
        assert result[1].refresh_token == "token2"
        mock_session.execute.assert_called_once()


# Дополнительные тесты для edge cases
class TestUserRepositoryEdgeCases:
    """Edge cases and validation tests"""
    
    @pytest.fixture
    def mock_session(self):
        session = AsyncMock(spec=AsyncSession)
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def user_repo(self, mock_session):
        return UserRepository(mock_session)
    
    @pytest.mark.asyncio
    async def test_create_user_rollback_on_error(self, user_repo, mock_session):
        """Test that rollback is called on database error during create"""
        # Arrange
        mock_session.commit.side_effect = SQLAlchemyError("Constraint violation")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repo.create(
                username="testuser",
                first_name="Test",
                family_name="User",
                email="test@example.com",
                hashed_password="hashed123"
            )
        
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_rollback_on_error(self, user_repo, mock_session):
        """Test that rollback is called on database error during update"""
        # Arrange
        mock_session.commit.side_effect = SQLAlchemyError("Update failed")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repo.update(1, first_name="Updated")
        
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_rollback_on_error(self, user_repo, mock_session):
        """Test that rollback is called on database error during delete"""
        # Arrange
        mock_session.commit.side_effect = SQLAlchemyError("Delete failed")
        
        # Act & Assert
        with pytest.raises(SQLAlchemyError):
            await user_repo.delete(1)
        
        mock_session.rollback.assert_called_once()
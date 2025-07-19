from typing import TypeVar, Generic, Type, Optional, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from .database import Base as DeclarativeBase
from sqlalchemy import inspect, select, delete, update
from sqlalchemy.exc import SQLAlchemyError
import logging


ModelType = TypeVar('ModelType', bound=DeclarativeBase)

logger = logging.getLogger(__name__)

class BaseRepository(Generic[ModelType]):
    """Base repository class for common CRUD operations."""
    
    def __init__(self, session: AsyncSession, model: Type[ModelType], primary_key_field: Optional[str] = None):
        self.session = session
        self.model = model

        self.primary_key_field = primary_key_field or self._get_primary_key_field()
    
    def _get_primary_key_field(self) -> str:
        """Get the primary key field name of the model."""
        try:
            mapper = inspect(self.model)
            primary_key_colomns = mapper.primary_key

            if len(primary_key_colomns) == 1:
                return primary_key_colomns[0].name
            elif len(primary_key_colomns) > 1:
                logger.warning(f"Model {self.model.__name__} has composite primary keys, using the first one: {primary_key_colomns[0].name}")
                return primary_key_colomns[0].name
            else:
                raise ValueError(f"Model {self.model.__name__} has no primary key defined.")
        except Exception as e:
            logger.error(f"Error getting primary key field for model {self.model.__name__}: {e}")
            return 'id'
    
    def _get_primary_key_column(self) -> Any:
        """Get the primary key column of the model."""
        return getattr(self.model, self.primary_key_field)

    async def get_by_id(self, id_value: Any) -> Optional[ModelType]:
        """Fetch a model instance by its primary key."""
        primary_key_column = self._get_primary_key_column()
        try:
            result = await self.session.execute(
                select(self.model).where(primary_key_column == id_value)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} by ID {id_value}: {e}")
            raise
    
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[ModelType]:
        """Fetch all model instances, with optional pagination."""
        try:
            query = select(self.model)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all {self.model.__name__} instances: {e}")
            raise
    
    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """Fetch a model instance by a specific field."""
        try:
            field_column = getattr(self.model, field_name)
            result = await self.session.execute(
                select(self.model).where(field_column == value)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} by field {field_name} with value {value}: {e}")
            raise
    
    async def get_by_fields(self, **filters) -> List[ModelType]:
        """Fetch model instances by multiple fields."""
        try:
            query = select(self.model)
            for field, value in filters.items():
                if hasattr(self.model, field):
                    field_column = getattr(self.model, field)
                    query = query.where(field_column == value)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} by fields {filters}: {e}")
            raise
    
    async def create(self, **object_data: Any) -> ModelType:
        """Create a new model instance."""
        try:
            obj = self.model(**object_data)
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def create_from_model(self, obj: ModelType) -> ModelType:
        """Create a new model instance from an existing model."""
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating {self.model.__name__} from model: {e}")
            raise
    
    async def update(self, id_value: Any, **update_data) -> Optional[ModelType]:
        """Update an existing model instance by its primary key."""
        try:
            primary_key_column = self._get_primary_key_column()
            stmt = (
                update(self.model)
                .where(primary_key_column == id_value)
                .values(**update_data)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.model.__name__} with ID {id_value}: {e}")
            raise
    
    async def delete(self, id_value: Any) -> bool:
        """Delete a model instance by its primary key."""
        try:
            primary_key_column = self._get_primary_key_column()
            stmt = delete(self.model).where(primary_key_column == id_value)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id_value}: {e}")
            raise
    
    async def delete_by_model(self, obj: ModelType) -> None:
        """Delete a model instance by passing the model object."""
        try:
            await self.session.delete(obj)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} by model: {e}")
            raise
    
    async def exists(self, id_value: Any) -> bool:
        """Check if a model instance exists by its primary key."""
        try:
            primary_key_column = self._get_primary_key_column()
            result = await self.session.execute(
                select(self.model).where(primary_key_column == id_value)
            )
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with ID {id_value}: {e}")
            raise
    
    async def count(self, **filters) -> int:
        """Count the number of model instances."""
        try:
            from sqlalchemy import func
            primary_key_column = self._get_primary_key_column()
            query = select(func.count(primary_key_column))

            for field, value in filters.items():
                if hasattr(self.model, field):
                    field_column = getattr(self.model, field)
                    query = query.where(field_column == value)
            
            result = await self.session.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__} instances: {e}")
            raise
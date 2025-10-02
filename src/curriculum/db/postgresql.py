"""PostgreSQL database adapter using SQLAlchemy."""

from typing import Any, Dict, List, Optional, Type
from uuid import UUID
import json

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Boolean, Float, Text, JSON, ForeignKey
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from curriculum.db.base import DatabaseInterface
from curriculum.core.base import BaseEntity
from curriculum.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy base class."""


# SQLAlchemy model definitions
class UserModel(Base):
    """User table model."""
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    language: Mapped[str] = mapped_column(String(10), default="en")
    roles: Mapped[str] = mapped_column(JSON, default=list)  # JSON array of role strings
    custom_permissions: Mapped[str] = mapped_column(JSON, default=list)
    last_login_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    last_activity_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    login_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    updated_at: Mapped[DateTime] = mapped_column(DateTime)
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class ContentModel(Base):
    """Content table model."""
    __tablename__ = "content"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50))
    format: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    content_body: Mapped[Optional[str]] = mapped_column(Text)
    content_url: Mapped[Optional[str]] = mapped_column(String(500))
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("content.id"))
    order_index: Mapped[int] = mapped_column(default=0)
    tags: Mapped[str] = mapped_column(JSON, default=list)
    keywords: Mapped[str] = mapped_column(JSON, default=list)
    author_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    contributors: Mapped[str] = mapped_column(JSON, default=list)
    current_version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    version_history: Mapped[str] = mapped_column(JSON, default=list)
    metadata_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    custom_metadata: Mapped[str] = mapped_column(JSON, default=dict)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    access_groups: Mapped[str] = mapped_column(JSON, default=list)
    view_count: Mapped[int] = mapped_column(default=0)
    download_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    updated_at: Mapped[DateTime] = mapped_column(DateTime)
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    author: Mapped["UserModel"] = relationship("UserModel", back_populates="content")
    parent: Mapped[Optional["ContentModel"]] = relationship("ContentModel", remote_side=[id])


class PostgreSQLAdapter(DatabaseInterface):
    """PostgreSQL database adapter."""

    def __init__(self) -> None:
        """Initialize PostgreSQL adapter."""
        self.engine = create_async_engine(settings.database_url)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self) -> None:
        """Connect to PostgreSQL database."""
        # Test connection
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def disconnect(self) -> None:
        """Disconnect from PostgreSQL database."""
        await self.engine.dispose()

    async def create(self, entity: BaseEntity) -> BaseEntity:
        """Create a new entity."""
        async with self.async_session() as session:
            # Convert Pydantic model to SQLAlchemy model
            sql_model = self._pydantic_to_sqlalchemy(entity)

            session.add(sql_model)
            await session.commit()
            await session.refresh(sql_model)

            # Convert back to Pydantic model
            return self._sqlalchemy_to_pydantic(sql_model, type(entity))

    async def get(self, entity_id: UUID, entity_type: Type[BaseEntity]) -> Optional[BaseEntity]:
        """Get entity by ID."""
        async with self.async_session() as session:
            # Map Pydantic type to SQLAlchemy model
            sql_model_class = self._get_sql_model_class(entity_type)

            result = await session.get(sql_model_class, entity_id)
            if result:
                return self._sqlalchemy_to_pydantic(result, entity_type)
        return None

    async def update(self, entity: BaseEntity) -> BaseEntity:
        """Update existing entity."""
        async with self.async_session() as session:
            sql_model_class = self._get_sql_model_class(type(entity))
            sql_model = await session.get(sql_model_class, entity.id)

            if sql_model:
                # Update fields
                for field_name, field_value in entity.model_dump(exclude_unset=True).items():
                    if hasattr(sql_model, field_name):
                        setattr(sql_model, field_name, field_value)

                await session.commit()
                await session.refresh(sql_model)

                return self._sqlalchemy_to_pydantic(sql_model, type(entity))
        return entity

    async def delete(self, entity_id: UUID, entity_type: Type[BaseEntity]) -> bool:
        """Delete entity."""
        async with self.async_session() as session:
            sql_model_class = self._get_sql_model_class(entity_type)
            sql_model = await session.get(sql_model_class, entity_id)

            if sql_model:
                await session.delete(sql_model)
                await session.commit()
                return True
        return False

    async def list(
        self,
        entity_type: Type[BaseEntity],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[BaseEntity]:
        """List entities with optional filtering and pagination."""
        async with self.async_session() as session:
            sql_model_class = self._get_sql_model_class(entity_type)

            query = select(sql_model_class)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(sql_model_class, field):
                        query = query.where(getattr(sql_model_class, field) == value)

            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await session.execute(query)
            sql_models = result.scalars().all()

            return [self._sqlalchemy_to_pydantic(model, entity_type) for model in sql_models]

    async def count(self, entity_type: Type[BaseEntity], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters."""
        async with self.async_session() as session:
            sql_model_class = self._get_sql_model_class(entity_type)

            query = select(sql_model_class)

            if filters:
                for field, value in filters.items():
                    if hasattr(sql_model_class, field):
                        query = query.where(getattr(sql_model_class, field) == value)

            result = await session.execute(query)
            return len(result.scalars().all())

    def _get_sql_model_class(self, entity_type: Type[BaseEntity]):
        """Map Pydantic model type to SQLAlchemy model class."""
        # This is a simplified mapping - in production you'd have a proper registry
        type_mapping = {
            # User: UserModel,
            # Content: ContentModel,
            # Add other mappings as needed
        }

        return type_mapping.get(entity_type)

    def _pydantic_to_sqlalchemy(self, entity: BaseEntity):
        """Convert Pydantic model to SQLAlchemy model."""
        # Simplified conversion - in production you'd handle this properly
        sql_model_class = self._get_sql_model_class(type(entity))
        data = entity.model_dump()

        return sql_model_class(**data)

    def _sqlalchemy_to_pydantic(self, sql_model, entity_type: Type[BaseEntity]) -> BaseEntity:
        """Convert SQLAlchemy model to Pydantic model."""
        # Simplified conversion - in production you'd handle this properly
        data = {}
        for column in sql_model.__table__.columns:
            value = getattr(sql_model, column.name)
            if isinstance(value, (list, dict)):
                value = json.loads(json.dumps(value))  # Convert to Python types
            data[column.name] = value

        return entity_type(**data)

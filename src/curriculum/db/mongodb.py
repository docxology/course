"""MongoDB database adapter."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from curriculum.config import settings
from curriculum.core.base import BaseEntity
from curriculum.db.base import DatabaseInterface, T


class MongoDBAdapter(DatabaseInterface):
    """MongoDB database adapter."""

    def __init__(self) -> None:
        """Initialize MongoDB adapter."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Connect to MongoDB database."""
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.database = self.client[settings.mongodb_db_name]

        # Test connection
        await self.client.admin.command("ping")

    async def disconnect(self) -> None:
        """Disconnect from MongoDB database."""
        if self.client:
            self.client.close()

    async def create(self, entity: T) -> T:
        """Create a new entity."""
        if self.database is None:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(type(entity))
        collection = self.database[collection_name]

        data = self._entity_to_dict(entity)
        data["_id"] = str(entity.id)  # Use string UUID as MongoDB _id

        await collection.insert_one(data)

        return entity

    async def get(self, entity_id: UUID, entity_type: Type[T]) -> Optional[T]:
        """Get entity by ID."""
        if self.database is None:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        document = await collection.find_one({"_id": str(entity_id)})

        if document:
            return self._dict_to_entity(document, entity_type)
        return None

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        if self.database is None:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(type(entity))
        collection = self.database[collection_name]

        data = self._entity_to_dict(entity)
        data["_id"] = str(entity.id)

        await collection.replace_one({"_id": str(entity.id)}, data, upsert=True)

        return entity

    async def delete(self, entity_id: UUID, entity_type: Type[T]) -> bool:
        """Delete entity."""
        if self.database is None:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        result = await collection.delete_one({"_id": str(entity_id)})

        return result.deleted_count > 0

    async def list(
        self,
        entity_type: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[T]:
        """List entities with optional filtering and pagination."""
        if self.database is None:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        query = filters or {}

        cursor = collection.find(query)

        if offset:
            cursor = cursor.skip(offset)
        if limit:
            cursor = cursor.limit(limit)

        documents = await cursor.to_list(length=None)

        return [self._dict_to_entity(doc, entity_type) for doc in documents]

    async def count(self, entity_type: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters."""
        if self.database is None:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        query = filters or {}

        return await collection.count_documents(query)

    def _get_collection_name(self, entity_type: Type[T]) -> str:
        """Get MongoDB collection name for entity type."""
        # Convert class name to snake_case collection name
        class_name = entity_type.__name__
        collection_name = ""

        for char in class_name:
            if char.isupper():
                collection_name += "_" + char.lower()
            else:
                collection_name += char

        # Remove leading underscore if present
        collection_name = collection_name.lstrip("_")

        return collection_name

    def _entity_to_dict(self, entity: BaseEntity) -> Dict[str, Any]:
        """Convert entity to dictionary for MongoDB storage."""
        data = entity.model_dump()
        data["_id"] = str(entity.id)

        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                # Handle nested structures recursively if needed
                pass

        return data

    def _dict_to_entity(self, data: Dict[str, Any], entity_type: Type[T]) -> T:
        """Convert MongoDB document to entity."""
        # Work on a copy so driver documents remain available to callers.
        values = dict(data)
        mongo_id = values.pop("_id", None)
        if mongo_id is not None:
            values["id"] = UUID(str(mongo_id))
        for key in ("created_at", "updated_at", "deleted_at"):
            value = values.get(key)
            if isinstance(value, str) and self._is_iso_datetime(value):
                values[key] = datetime.fromisoformat(value)
        return entity_type(**values)

    def _is_iso_datetime(self, value: str) -> bool:
        """Check if string is ISO datetime format."""
        try:
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False

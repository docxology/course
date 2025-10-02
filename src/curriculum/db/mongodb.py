"""MongoDB database adapter."""

from typing import Any, Dict, List, Optional, Type
from uuid import UUID
from datetime import datetime
import json

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ReturnDocument

from curriculum.db.base import DatabaseInterface
from curriculum.core.base import BaseEntity
from curriculum.config import settings


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
        await self.client.admin.command('ping')

    async def disconnect(self) -> None:
        """Disconnect from MongoDB database."""
        if self.client:
            self.client.close()

    async def create(self, entity: BaseEntity) -> BaseEntity:
        """Create a new entity."""
        if not self.database:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(type(entity))
        collection = self.database[collection_name]

        data = self._entity_to_dict(entity)
        data["_id"] = str(entity.id)  # Use string UUID as MongoDB _id

        await collection.insert_one(data)

        return entity

    async def get(self, entity_id: UUID, entity_type: Type[BaseEntity]) -> Optional[BaseEntity]:
        """Get entity by ID."""
        if not self.database:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        document = await collection.find_one({"_id": str(entity_id)})

        if document:
            return self._dict_to_entity(document, entity_type)
        return None

    async def update(self, entity: BaseEntity) -> BaseEntity:
        """Update existing entity."""
        if not self.database:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(type(entity))
        collection = self.database[collection_name]

        data = self._entity_to_dict(entity)
        data["_id"] = str(entity.id)

        await collection.replace_one(
            {"_id": str(entity.id)},
            data,
            upsert=True
        )

        return entity

    async def delete(self, entity_id: UUID, entity_type: Type[BaseEntity]) -> bool:
        """Delete entity."""
        if not self.database:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        result = await collection.delete_one({"_id": str(entity_id)})

        return result.deleted_count > 0

    async def list(
        self,
        entity_type: Type[BaseEntity],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[BaseEntity]:
        """List entities with optional filtering and pagination."""
        if not self.database:
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

    async def count(self, entity_type: Type[BaseEntity], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters."""
        if not self.database:
            raise RuntimeError("Database not connected")

        collection_name = self._get_collection_name(entity_type)
        collection = self.database[collection_name]

        query = filters or {}

        return await collection.count_documents(query)

    def _get_collection_name(self, entity_type: Type[BaseEntity]) -> str:
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

        # Convert datetime objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                # Handle nested structures recursively if needed
                pass

        return data

    def _dict_to_entity(self, data: Dict[str, Any], entity_type: Type[BaseEntity]) -> BaseEntity:
        """Convert MongoDB document to entity."""
        # Convert ISO datetime strings back to datetime objects
        for key, value in data.items():
            if isinstance(value, str) and self._is_iso_datetime(value):
                data[key] = datetime.fromisoformat(value)
            elif key == "_id":
                data["id"] = UUID(data["_id"])
                del data["_id"]

        return entity_type(**data)

    def _is_iso_datetime(self, value: str) -> bool:
        """Check if string is ISO datetime format."""
        try:
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False

"""Database base classes and interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from uuid import UUID

from curriculum.core.base import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class DatabaseInterface(ABC):
    """Abstract base class for database operations."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to database."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from database."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def get(self, entity_id: UUID, entity_type: Type[T]) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID, entity_type: Type[T]) -> bool:
        """Delete entity."""
        pass

    @abstractmethod
    async def list(
        self,
        entity_type: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[T]:
        """List entities with optional filtering and pagination."""
        pass

    @abstractmethod
    async def count(self, entity_type: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters."""
        pass


class DatabaseManager:
    """Database manager for handling multiple database connections."""

    def __init__(self) -> None:
        """Initialize database manager."""
        self._databases: Dict[str, DatabaseInterface] = {}
        self._default_db: Optional[str] = None

    def register_database(self, name: str, db: DatabaseInterface, default: bool = False) -> None:
        """Register a database instance."""
        self._databases[name] = db
        if default or self._default_db is None:
            self._default_db = name

    def get_database(self, name: Optional[str] = None) -> DatabaseInterface:
        """Get database instance."""
        db_name = name or self._default_db
        if db_name not in self._databases:
            raise ValueError(f"Database '{db_name}' not registered")
        return self._databases[db_name]

    async def initialize_all(self) -> None:
        """Initialize all registered databases."""
        for db in self._databases.values():
            await db.connect()

    async def shutdown_all(self) -> None:
        """Shutdown all registered databases."""
        for db in self._databases.values():
            await db.disconnect()


# Global database manager instance
db_manager = DatabaseManager()

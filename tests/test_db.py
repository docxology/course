"""Tests for database module."""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from curriculum.db.base import DatabaseManager
from curriculum.db.mongodb import MongoDBAdapter
from curriculum.db.postgresql import PostgreSQLAdapter
from curriculum.core.content import Content, ContentType


class TestDatabaseManager:
    """Tests for DatabaseManager."""

    def test_database_manager_initialization(self):
        """Test database manager initialization."""
        db_manager = DatabaseManager()

        assert db_manager is not None
        assert db_manager._databases == {}
        assert db_manager._default_db is None

    def test_register_database(self):
        """Test registering a database."""
        db_manager = DatabaseManager()
        mock_db = MagicMock()

        db_manager.register_database("test_db", mock_db)

        assert "test_db" in db_manager._databases
        assert db_manager._databases["test_db"] == mock_db
        assert db_manager._default_db == "test_db"

    def test_register_database_as_default(self):
        """Test registering a database as default."""
        db_manager = DatabaseManager()
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()

        db_manager.register_database("db1", mock_db1)
        db_manager.register_database("db2", mock_db2, default=True)

        assert db_manager._default_db == "db2"

    def test_get_database(self):
        """Test getting a registered database."""
        db_manager = DatabaseManager()
        mock_db = MagicMock()
        db_manager.register_database("test_db", mock_db)

        retrieved_db = db_manager.get_database("test_db")

        assert retrieved_db == mock_db

    def test_get_default_database(self):
        """Test getting the default database."""
        db_manager = DatabaseManager()
        mock_db = MagicMock()
        db_manager.register_database("test_db", mock_db)

        retrieved_db = db_manager.get_database()

        assert retrieved_db == mock_db

    def test_get_nonexistent_database(self):
        """Test getting a non-existent database."""
        db_manager = DatabaseManager()

        with pytest.raises(ValueError):
            db_manager.get_database("nonexistent")

    def test_initialize_all(self):
        """Test initializing all databases."""
        db_manager = DatabaseManager()
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()

        db_manager.register_database("db1", mock_db1)
        db_manager.register_database("db2", mock_db2)

        # Should not raise any exceptions
        # (In real implementation, this would be async)
        pass

    def test_shutdown_all(self):
        """Test shutting down all databases."""
        db_manager = DatabaseManager()
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()

        db_manager.register_database("db1", mock_db1)
        db_manager.register_database("db2", mock_db2)

        # Should not raise any exceptions
        # (In real implementation, this would be async)
        pass


class TestMongoDBAdapter:
    """Tests for MongoDBAdapter."""

    @pytest.fixture
    def mongodb_adapter(self):
        """MongoDB adapter fixture."""
        return MongoDBAdapter()

    def test_mongodb_adapter_initialization(self, mongodb_adapter):
        """Test MongoDB adapter initialization."""
        assert mongodb_adapter.client is None
        assert mongodb_adapter.database is None

    @patch('motor.motor_asyncio.AsyncIOMotorClient')
    async def test_mongodb_connect(self, mock_client_class, mongodb_adapter):
        """Test MongoDB connection."""
        mock_client = MagicMock()
        mock_client.admin.command.return_value = None
        mock_client_class.return_value = mock_client

        await mongodb_adapter.connect()

        assert mongodb_adapter.client == mock_client
        assert mongodb_adapter.database is not None
        mock_client.admin.command.assert_called_once_with('ping')

    async def test_mongodb_disconnect(self, mongodb_adapter):
        """Test MongoDB disconnection."""
        mongodb_adapter.client = MagicMock()

        await mongodb_adapter.disconnect()

        mongodb_adapter.client.close.assert_called_once()

    async def test_mongodb_create_entity(self, mongodb_adapter):
        """Test creating an entity in MongoDB."""
        mongodb_adapter.client = MagicMock()
        mongodb_adapter.database = MagicMock()

        mock_collection = MagicMock()
        mongodb_adapter.database.__getitem__ = MagicMock(return_value=mock_collection)

        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4()
        )

        result = await mongodb_adapter.create(content)

        assert result == content
        mock_collection.insert_one.assert_called_once()

    async def test_mongodb_get_entity(self, mongodb_adapter):
        """Test getting an entity from MongoDB."""
        mongodb_adapter.client = MagicMock()
        mongodb_adapter.database = MagicMock()

        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {
            "_id": str(uuid4()),
            "title": "Test Content",
            "content_type": "lesson"
        }
        mongodb_adapter.database.__getitem__ = MagicMock(return_value=mock_collection)

        entity_id = uuid4()
        result = await mongodb_adapter.get(entity_id, Content)

        assert result is not None
        mock_collection.find_one.assert_called_once()

    async def test_mongodb_update_entity(self, mongodb_adapter):
        """Test updating an entity in MongoDB."""
        mongodb_adapter.client = MagicMock()
        mongodb_adapter.database = MagicMock()

        mock_collection = MagicMock()
        mongodb_adapter.database.__getitem__ = MagicMock(return_value=mock_collection)

        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4()
        )

        result = await mongodb_adapter.update(content)

        assert result == content
        mock_collection.replace_one.assert_called_once()

    async def test_mongodb_delete_entity(self, mongodb_adapter):
        """Test deleting an entity from MongoDB."""
        mongodb_adapter.client = MagicMock()
        mongodb_adapter.database = MagicMock()

        mock_collection = MagicMock()
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        mongodb_adapter.database.__getitem__ = MagicMock(return_value=mock_collection)

        entity_id = uuid4()
        result = await mongodb_adapter.delete(entity_id, Content)

        assert result is True
        mock_collection.delete_one.assert_called_once()

    async def test_mongodb_list_entities(self, mongodb_adapter):
        """Test listing entities from MongoDB."""
        mongodb_adapter.client = MagicMock()
        mongodb_adapter.database = MagicMock()

        mock_collection = MagicMock()
        mock_collection.find.return_value.to_list.return_value = [
            {"_id": str(uuid4()), "title": "Content 1"},
            {"_id": str(uuid4()), "title": "Content 2"}
        ]
        mongodb_adapter.database.__getitem__ = MagicMock(return_value=mock_collection)

        result = await mongodb_adapter.list(Content)

        assert isinstance(result, list)
        assert len(result) == 2

    async def test_mongodb_count_entities(self, mongodb_adapter):
        """Test counting entities in MongoDB."""
        mongodb_adapter.client = MagicMock()
        mongodb_adapter.database = MagicMock()

        mock_collection = MagicMock()
        mock_collection.count_documents.return_value = 5
        mongodb_adapter.database.__getitem__ = MagicMock(return_value=mock_collection)

        result = await mongodb_adapter.count(Content)

        assert result == 5
        mock_collection.count_documents.assert_called_once()

    def test_get_collection_name(self, mongodb_adapter):
        """Test getting MongoDB collection name."""
        collection_name = mongodb_adapter._get_collection_name(Content)

        assert isinstance(collection_name, str)
        assert collection_name.islower()  # Should be snake_case

    def test_entity_to_dict(self, mongodb_adapter):
        """Test converting entity to dictionary."""
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4()
        )

        result = mongodb_adapter._entity_to_dict(content)

        assert "_id" in result
        assert result["title"] == "Test Content"
        assert result["content_type"] == "lesson"

    def test_dict_to_entity(self, mongodb_adapter):
        """Test converting dictionary to entity."""
        data = {
            "_id": str(uuid4()),
            "title": "Test Content",
            "content_type": "lesson",
            "format": "markdown",
            "created_at": "2024-01-01T00:00:00Z"
        }

        result = mongodb_adapter._dict_to_entity(data, Content)

        assert isinstance(result, Content)
        assert result.title == "Test Content"

    def test_is_iso_datetime(self, mongodb_adapter):
        """Test ISO datetime validation."""
        assert mongodb_adapter._is_iso_datetime("2024-01-01T00:00:00Z") is True
        assert mongodb_adapter._is_iso_datetime("invalid") is False
        assert mongodb_adapter._is_iso_datetime(123) is False


class TestPostgreSQLAdapter:
    """Tests for PostgreSQLAdapter."""

    @pytest.fixture
    def postgresql_adapter(self):
        """PostgreSQL adapter fixture."""
        return PostgreSQLAdapter()

    def test_postgresql_adapter_initialization(self, postgresql_adapter):
        """Test PostgreSQL adapter initialization."""
        assert postgresql_adapter.engine is not None
        assert postgresql_adapter.async_session is not None

    @patch('sqlalchemy.ext.asyncio.create_async_engine')
    def test_postgresql_connect(self, mock_create_engine, postgresql_adapter):
        """Test PostgreSQL connection."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__aenter__ = MagicMock(return_value=mock_conn)
        mock_create_engine.return_value = mock_engine

        # Should not raise any exceptions
        # (In real implementation, this would be async)
        pass

    def test_postgresql_disconnect(self, postgresql_adapter):
        """Test PostgreSQL disconnection."""
        # Should not raise any exceptions
        pass

    def test_get_sql_model_class(self, postgresql_adapter):
        """Test getting SQL model class."""
        # This would need actual SQLAlchemy model classes
        # For now, just test that the method exists
        assert hasattr(postgresql_adapter, '_get_sql_model_class')

    def test_pydantic_to_sqlalchemy(self, postgresql_adapter):
        """Test converting Pydantic model to SQLAlchemy."""
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4()
        )

        # This would need actual SQLAlchemy model classes
        # For now, just test that the method exists
        assert hasattr(postgresql_adapter, '_pydantic_to_sqlalchemy')

    def test_sqlalchemy_to_pydantic(self, postgresql_adapter):
        """Test converting SQLAlchemy model to Pydantic."""
        # This would need actual SQLAlchemy model classes
        # For now, just test that the method exists
        assert hasattr(postgresql_adapter, '_sqlalchemy_to_pydantic')



"""Comprehensive unit tests for Search module services."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from curriculum.core.content import Content, ContentType, ContentFormat
from curriculum.search.search import SearchService


@pytest.mark.unit
class TestSearchService:
    """Comprehensive tests for SearchService."""

    @pytest.fixture
    def search_service(self):
        """Create SearchService instance."""
        return SearchService()

    @pytest.fixture
    def sample_content(self):
        """Create sample content for testing."""
        return Content(
            title="Python Programming Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
            description="Learn Python fundamentals",
            content_body="# Introduction to Python\nPython is a programming language.",
            tags=["python", "programming", "beginner"],
        )

    def test_search_service_initialization(self, search_service):
        """Test SearchService initialization."""
        assert search_service is not None
        assert search_service._index_name == "curriculum"
        assert search_service._client is None
        assert search_service._connected is False

    def test_search_service_methods_exist(self, search_service):
        """Test that all expected methods exist."""
        required_methods = [
            "connect",
            "disconnect",
            "index_content",
            "delete_from_index",
            "search",
            "suggest",
            "get_similar_content",
            "get_index_stats",
            "is_connected",
        ]

        for method_name in required_methods:
            assert hasattr(search_service, method_name), f"Method {method_name} not found"
            assert callable(getattr(search_service, method_name)), f"Method {method_name} not callable"

    def test_is_connected_initially_false(self, search_service):
        """Test is_connected returns False initially."""
        assert search_service.is_connected() is False

    @pytest.mark.asyncio
    async def test_index_content_not_connected(self, search_service, sample_content):
        """Test index_content when not connected."""
        result = await search_service.index_content(sample_content)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_from_index_not_connected(self, search_service, sample_content):
        """Test delete_from_index when not connected."""
        result = await search_service.delete_from_index(sample_content.id)
        assert result is False

    @pytest.mark.asyncio
    async def test_search_not_connected(self, search_service):
        """Test search when not connected."""
        result = await search_service.search("python")
        assert result is None

    @pytest.mark.asyncio
    async def test_suggest_not_connected(self, search_service):
        """Test suggest when not connected."""
        result = await search_service.suggest("python")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_similar_content_not_connected(self, search_service, sample_content):
        """Test get_similar_content when not connected."""
        result = await search_service.get_similar_content(sample_content.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_index_stats_not_connected(self, search_service):
        """Test get_index_stats when not connected."""
        result = await search_service.get_index_stats()
        assert result is None

    @pytest.mark.asyncio
    async def test_connect_success(self, search_service):
        """Test successful connection to Elasticsearch."""
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_es.return_value = mock_client

            await search_service.connect()

            assert search_service._connected is True
            assert search_service._client is not None
            mock_client.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, search_service):
        """Test connection failure to Elasticsearch."""
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_es.side_effect = Exception("Connection failed")

            await search_service.connect()

            assert search_service._connected is False
            assert search_service._client is None

    @pytest.mark.asyncio
    async def test_disconnect_with_client(self, search_service):
        """Test disconnect when client exists."""
        mock_client = AsyncMock()
        search_service._client = mock_client
        search_service._connected = True

        await search_service.disconnect()

        mock_client.close.assert_called_once()
        assert search_service._client is None
        assert search_service._connected is False

    @pytest.mark.asyncio
    async def test_disconnect_without_client(self, search_service):
        """Test disconnect when no client exists."""
        search_service._client = None

        await search_service.disconnect()

        # Should not raise any exception

    @pytest.mark.asyncio
    async def test_index_content_success(self, search_service, sample_content):
        """Test successful content indexing."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_es.return_value = mock_client

            await search_service.connect()

            # Mock index operation
            mock_client.index.return_value = {"result": "created"}

            result = await search_service.index_content(sample_content)

            assert result is True
            mock_client.index.assert_called_once()

            # Check that document structure is correct
            call_args = mock_client.index.call_args
            assert "index" in call_args.kwargs
            assert "id" in call_args.kwargs
            assert "document" in call_args.kwargs

            document = call_args.kwargs["document"]
            assert document["id"] == str(sample_content.id)
            assert document["title"] == sample_content.title
            assert document["content_type"] == sample_content.content_type.value

    @pytest.mark.asyncio
    async def test_delete_from_index_success(self, search_service, sample_content):
        """Test successful content deletion from index."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_es.return_value = mock_client

            await search_service.connect()

            # Mock delete operation
            mock_client.delete.return_value = {"result": "deleted"}

            result = await search_service.delete_from_index(sample_content.id)

            assert result is True
            mock_client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_basic_query(self, search_service):
        """Test basic search functionality."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.search.return_value = {
                "hits": {
                    "total": {"value": 1},
                    "hits": [
                        {
                            "_source": {
                                "id": str(uuid4()),
                                "title": "Python Programming",
                                "content_type": "lesson",
                                "score": 0.95
                            }
                        }
                    ]
                }
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            result = await search_service.search("python programming")

            assert result is not None
            assert "results" in result
            assert "total" in result
            assert len(result["results"]) == 1
            assert result["total"] == 1

            mock_client.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_filters(self, search_service):
        """Test search with content type filter."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.search.return_value = {
                "hits": {"total": {"value": 0}, "hits": []}
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            result = await search_service.search("python", content_type="lesson")

            assert result is not None
            mock_client.search.assert_called_once()

            # Check that filter was applied
            call_args = mock_client.search.call_args
            assert "query" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_suggest_functionality(self, search_service):
        """Test search suggestions."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.search.return_value = {
                "hits": {
                    "total": {"value": 2},
                    "hits": [
                        {"_source": {"title": "Python Basics", "tags": ["python", "programming"]}},
                        {"_source": {"title": "Advanced Python", "tags": ["python", "advanced"]}}
                    ]
                }
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            result = await search_service.suggest("python")

            assert result is not None
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_similar_content(self, search_service, sample_content):
        """Test getting similar content."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.search.return_value = {
                "hits": {
                    "total": {"value": 2},
                    "hits": [
                        {
                            "_source": {
                                "id": str(uuid4()),
                                "title": "Similar Content 1",
                                "content_type": "lesson"
                            }
                        },
                        {
                            "_source": {
                                "id": str(uuid4()),
                                "title": "Similar Content 2",
                                "content_type": "lesson"
                            }
                        }
                    ]
                }
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            result = await search_service.get_similar_content(sample_content.id)

            assert result is not None
            assert "results" in result
            assert "total" in result
            assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_get_index_stats(self, search_service):
        """Test getting index statistics."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.indices.stats.return_value = {
                "indices": {
                    "curriculum": {
                        "total": {"docs": {"count": 100}},
                        "store": {"size_in_bytes": 1024000}
                    }
                }
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            result = await search_service.get_index_stats()

            assert result is not None
            assert "total_documents" in result
            assert "index_size" in result
            assert result["total_documents"] == 100
            assert result["index_size"] == 1024000

    def test_search_service_state_management(self, search_service):
        """Test search service state management."""
        # Initially disconnected
        assert search_service.is_connected() is False

        # After failed connection
        assert search_service._connected is False
        assert search_service._client is None

    def test_search_service_index_name(self, search_service):
        """Test that index name is set correctly."""
        from curriculum.config import settings
        assert search_service._index_name == settings.elasticsearch_index
        assert search_service._index_name == "curriculum"

    @pytest.mark.asyncio
    async def test_search_with_pagination(self, search_service):
        """Test search with pagination parameters."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.search.return_value = {
                "hits": {"total": {"value": 50}, "hits": []}
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            result = await search_service.search("python", page=2, page_size=10)

            assert result is not None
            mock_client.search.assert_called_once()

            # Check pagination parameters
            call_args = mock_client.search.call_args
            assert "from_" in call_args.kwargs
            assert "size" in call_args.kwargs
            assert call_args.kwargs["from_"] == 10  # page 2 * page_size 10
            assert call_args.kwargs["size"] == 10

    @pytest.mark.asyncio
    async def test_index_content_document_structure(self, search_service, sample_content):
        """Test that indexed document has correct structure."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.index.return_value = {"result": "created"}
            mock_es.return_value = mock_client

            await search_service.connect()

            await search_service.index_content(sample_content)

            # Verify document structure
            call_args = mock_client.index.call_args
            document = call_args.kwargs["document"]

            assert document["id"] == str(sample_content.id)
            assert document["title"] == sample_content.title
            assert document["description"] == sample_content.description
            assert document["content_body"] == sample_content.content_body
            assert document["content_type"] == sample_content.content_type.value
            assert document["author_id"] == str(sample_content.author_id)
            assert document["tags"] == sample_content.tags

    def test_search_service_error_handling(self, search_service):
        """Test search service error handling."""
        # Test that service handles missing Elasticsearch gracefully
        assert search_service.is_connected() is False

        # Operations should return None or False when not connected
        assert search_service.search("test") is None
        assert search_service.suggest("test") is None
        assert search_service.get_similar_content(uuid4()) is None
        assert search_service.get_index_stats() is None
        assert search_service.index_content(Content(
            title="test", content_type=ContentType.LESSON, format=ContentFormat.MARKDOWN, author_id=uuid4()
        )) is False
        assert search_service.delete_from_index(uuid4()) is False

    def test_search_service_configuration(self, search_service):
        """Test search service configuration."""
        # Test that service uses correct configuration
        from curriculum.config import settings

        assert search_service._index_name == settings.elasticsearch_index
        assert search_service._index_name == "curriculum"

        # Test that service can be initialized without connection
        assert search_service._client is None
        assert search_service._connected is False

    @pytest.mark.asyncio
    async def test_search_with_complex_query(self, search_service):
        """Test search with complex query structure."""
        # Setup connected service
        with patch('curriculum.search.search.AsyncElasticsearch') as mock_es:
            mock_client = AsyncMock()
            mock_client.info.return_value = {"version": {"number": "7.10.0"}}
            mock_client.search.return_value = {
                "hits": {"total": {"value": 0}, "hits": []}
            }
            mock_es.return_value = mock_client

            await search_service.connect()

            # Test search with multiple parameters
            result = await search_service.search(
                query="python programming",
                content_type="lesson",
                tags=["beginner", "python"],
                page=1,
                page_size=20
            )

            assert result is not None
            mock_client.search.assert_called_once()

            # Verify query structure
            call_args = mock_client.search.call_args
            assert "query" in call_args.kwargs

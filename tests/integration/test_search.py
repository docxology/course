"""Tests for search module."""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from curriculum.core.content import Content, ContentType
from curriculum.search.search import SearchService
from curriculum.search.visualization import VisualizationService
from curriculum.search.website import WebsiteService


@pytest.mark.integration
class TestSearchService:
    """Tests for SearchService."""

    @pytest.fixture
    def search_service(self):
        """Search service fixture."""
        return SearchService()

    def test_search_service_initialization(self, search_service):
        """Test search service initialization."""
        assert search_service is not None
        assert hasattr(search_service, '_index_name')
        assert hasattr(search_service, '_client')
        assert hasattr(search_service, '_connected')

    @patch('elasticsearch.AsyncElasticsearch')
    async def test_search_connect(self, mock_es_class, search_service):
        """Test Elasticsearch connection."""
        mock_client = MagicMock()
        mock_client.info.return_value = {"version": {"number": "8.0.0"}}
        mock_es_class.return_value = mock_client

        await search_service.connect()

        assert search_service._connected is True
        assert search_service._client == mock_client

    async def test_search_disconnect(self, search_service):
        """Test Elasticsearch disconnection."""
        search_service._client = MagicMock()

        await search_service.disconnect()

        search_service._client.close.assert_called_once()

    async def test_index_content(self, search_service):
        """Test content indexing."""
        search_service._connected = True
        search_service._client = MagicMock()

        mock_client = search_service._client
        mock_client.index.return_value = None

        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4(),
            content_body="This is test content for indexing."
        )

        result = await search_service.index_content(content)

        assert result is True
        mock_client.index.assert_called_once()

    async def test_delete_from_index(self, search_service):
        """Test content deletion from index."""
        search_service._connected = True
        search_service._client = MagicMock()

        mock_client = search_service._client
        mock_client.delete.return_value = None

        content_id = uuid4()
        result = await search_service.delete_from_index(content_id)

        assert result is True
        mock_client.delete.assert_called_once()

    async def test_search_content(self, search_service):
        """Test content search."""
        search_service._connected = True
        search_service._client = MagicMock()

        mock_client = search_service._client
        mock_client.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "max_score": 1.0,
                "hits": [
                    {
                        "_source": {
                            "id": str(uuid4()),
                            "title": "Test Content",
                            "content_type": "lesson"
                        },
                        "_score": 1.0
                    }
                ]
            }
        }

        result = await search_service.search("test query")

        assert "total" in result
        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Content"

    async def test_suggest_search(self, search_service):
        """Test search suggestions."""
        search_service._connected = True
        search_service._client = MagicMock()

        mock_client = search_service._client
        mock_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "title": "Python Programming",
                            "tags": ["python", "programming"]
                        }
                    }
                ]
            }
        }

        suggestions = await search_service.suggest("python")

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    async def test_similar_content(self, search_service):
        """Test finding similar content."""
        search_service._connected = True
        search_service._client = MagicMock()

        mock_client = search_service._client
        mock_client.search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "id": str(uuid4()),
                            "title": "Similar Content",
                            "content_type": "lesson"
                        },
                        "_score": 0.8
                    }
                ]
            }
        }

        content_id = uuid4()
        similar = await search_service.get_similar_content(content_id)

        assert isinstance(similar, list)
        assert len(similar) > 0

    async def test_get_index_stats(self, search_service):
        """Test getting index statistics."""
        search_service._connected = True
        search_service._client = MagicMock()

        mock_client = search_service._client
        mock_client.indices.stats.return_value = {
            "indices": {
                "curriculum": {
                    "total": {
                        "docs": {"count": 100},
                        "store": {"size_in_bytes": 1024000}
                    }
                }
            }
        }

        stats = await search_service.get_index_stats()

        assert "index_name" in stats
        assert "total_docs" in stats
        assert "size_in_bytes" in stats

    def test_search_service_not_connected(self):
        """Test search service when not connected."""
        search_service = SearchService()
        # Don't connect the service

        # Should return error responses
        result = search_service.search("test")
        assert "error" in result

        suggestions = search_service.suggest("test")
        assert suggestions == []

        similar = search_service.get_similar_content(uuid4())
        assert similar == []


@pytest.mark.integration
class TestVisualizationService:
    """Tests for VisualizationService."""

    @pytest.fixture
    def visualization_service(self):
        """Visualization service fixture."""
        return VisualizationService()

    def test_visualization_service_initialization(self, visualization_service):
        """Test visualization service initialization."""
        assert visualization_service is not None
        assert hasattr(visualization_service, '_visualizations')
        assert hasattr(visualization_service, '_chart_templates')

    def test_create_visualization(self, visualization_service):
        """Test creating a visualization."""
        content_id = uuid4()

        visualization = visualization_service.create_visualization(
            content_id=content_id,
            title="Test Chart",
            visualization_type="bar_chart",
            data={"labels": ["A", "B"], "datasets": [{"data": [1, 2]}]}
        )

        assert visualization["content_id"] == str(content_id)
        assert visualization["title"] == "Test Chart"
        assert visualization["type"] == "bar_chart"
        assert visualization["is_interactive"] is True

    def test_get_visualization(self, visualization_service):
        """Test getting a visualization."""
        content_id = uuid4()

        # Create a visualization first
        viz = visualization_service.create_visualization(
            content_id=content_id,
            title="Test Chart",
            visualization_type="line_chart",
            data={}
        )

        # Retrieve it
        retrieved = visualization_service.get_visualization(viz["id"])

        assert retrieved is not None
        assert retrieved["id"] == viz["id"]

    def test_get_content_visualizations(self, visualization_service):
        """Test getting visualizations for content."""
        content_id = uuid4()

        # Create multiple visualizations
        for i in range(3):
            visualization_service.create_visualization(
                content_id=content_id,
                title=f"Chart {i}",
                visualization_type="bar_chart",
                data={}
            )

        visualizations = visualization_service.get_content_visualizations(content_id)

        assert isinstance(visualizations, list)
        assert len(visualizations) >= 3

    def test_create_progress_chart(self, visualization_service):
        """Test creating progress chart."""
        content_id = uuid4()
        user_id = uuid4()

        chart = visualization_service.create_progress_chart(
            content_id=content_id,
            user_id=user_id,
            progress_data={"dates": ["2024-01-01"], "scores": [85]}
        )

        assert chart["content_id"] == str(content_id)
        assert chart["title"] == "Learning Progress"
        assert chart["type"] == "line_chart"

    def test_create_knowledge_map(self, visualization_service):
        """Test creating knowledge map."""
        content_id = uuid4()

        concepts = [
            {"id": "concept1", "label": "Variables"},
            {"id": "concept2", "label": "Functions"}
        ]
        connections = [
            {"source": "concept1", "target": "concept2", "type": "prerequisite"}
        ]

        knowledge_map = visualization_service.create_knowledge_map(
            content_id=content_id,
            concepts=concepts,
            connections=connections
        )

        assert knowledge_map["content_id"] == str(content_id)
        assert knowledge_map["title"] == "Knowledge Map"
        assert knowledge_map["type"] == "network_graph"

    def test_create_quiz_results_chart(self, visualization_service):
        """Test creating quiz results chart."""
        content_id = uuid4()

        quiz_results = {
            "quiz_names": ["Quiz 1", "Quiz 2"],
            "scores": [85, 92]
        }

        chart = visualization_service.create_quiz_results_chart(
            content_id=content_id,
            quiz_results=quiz_results
        )

        assert chart["content_id"] == str(content_id)
        assert chart["title"] == "Quiz Performance"
        assert chart["type"] == "bar_chart"

    def test_get_visualization_types(self, visualization_service):
        """Test getting visualization types."""
        types = visualization_service.get_visualization_types()

        assert isinstance(types, list)
        assert "bar_chart" in types
        assert "line_chart" in types
        assert "pie_chart" in types

    def test_export_visualization(self, visualization_service):
        """Test exporting visualization."""
        content_id = uuid4()

        # Create a visualization first
        viz = visualization_service.create_visualization(
            content_id=content_id,
            title="Test Chart",
            visualization_type="line_chart",
            data={}
        )

        # Export it
        exported = visualization_service.export_visualization(
            visualization_id=viz["id"],
            format="json"
        )

        assert exported["id"] == viz["id"]
        assert exported["format"] == "json"

    def test_validate_visualization_data(self, visualization_service):
        """Test visualization data validation."""
        valid_data = {
            "labels": ["A", "B"],
            "datasets": [{"data": [1, 2]}]
        }
        invalid_data = {"invalid": "data"}

        valid_result = visualization_service.validate_visualization_data(valid_data, "bar_chart")
        invalid_result = visualization_service.validate_visualization_data(invalid_data, "bar_chart")

        assert valid_result["valid"] is True
        assert invalid_result["valid"] is False


@pytest.mark.integration
class TestWebsiteService:
    """Tests for WebsiteService."""

    @pytest.fixture
    def website_service(self):
        """Website service fixture."""
        return WebsiteService()

    def test_website_service_initialization(self, website_service):
        """Test website service initialization."""
        assert website_service is not None
        assert hasattr(website_service, '_sites')
        assert hasattr(website_service, '_pages')
        assert hasattr(website_service, '_themes')

    def test_create_course_website(self, website_service):
        """Test creating course website."""
        course_id = uuid4()
        instructor_id = uuid4()

        website = website_service.create_course_website(
            course_id=course_id,
            title="Test Course",
            description="A test course website",
            instructor_id=instructor_id
        )

        assert website["course_id"] == str(course_id)
        assert website["title"] == "Test Course"
        assert website["instructor_id"] == str(instructor_id)
        assert website["is_public"] is False

    def test_get_course_website(self, website_service):
        """Test getting course website."""
        course_id = uuid4()

        # Create a website first
        website_service.create_course_website(
            course_id=course_id,
            title="Test Course",
            description="Test",
            instructor_id=uuid4()
        )

        # Retrieve it
        retrieved = website_service.get_course_website(course_id)

        assert retrieved is not None
        assert retrieved["course_id"] == str(course_id)

    def test_create_page(self, website_service):
        """Test creating a website page."""
        site_id = uuid4()

        page = website_service.create_page(
            site_id=site_id,
            title="Test Page",
            content="This is test page content",
            page_type="lesson"
        )

        assert page["site_id"] == str(site_id)
        assert page["title"] == "Test Page"
        assert page["content"] == "This is test page content"
        assert page["page_type"] == "lesson"

    def test_get_site_pages(self, website_service):
        """Test getting site pages."""
        site_id = uuid4()

        # Create some pages
        for i in range(3):
            website_service.create_page(
                site_id=site_id,
                title=f"Page {i}",
                content=f"Content {i}",
                page_type="lesson"
            )

        pages = website_service.get_site_pages(site_id)

        assert isinstance(pages, list)
        assert len(pages) >= 3

    def test_generate_student_dashboard(self, website_service):
        """Test generating student dashboard."""
        user_id = uuid4()
        course_id = uuid4()

        dashboard = website_service.generate_student_dashboard(user_id, course_id)

        assert dashboard["user_id"] == str(user_id)
        assert dashboard["course_id"] == str(course_id)
        assert "overall_progress" in dashboard
        assert "recent_activity" in dashboard

    def test_generate_instructor_dashboard(self, website_service):
        """Test generating instructor dashboard."""
        instructor_id = uuid4()
        course_id = uuid4()

        dashboard = website_service.generate_instructor_dashboard(instructor_id, course_id)

        assert dashboard["instructor_id"] == str(instructor_id)
        assert dashboard["course_id"] == str(course_id)
        assert "enrolled_students" in dashboard
        assert "pending_grades" in dashboard

    def test_create_announcement(self, website_service):
        """Test creating website announcement."""
        site_id = uuid4()
        author_id = uuid4()

        announcement = website_service.create_announcement(
            site_id=site_id,
            title="Important Announcement",
            content="This is an important announcement",
            author_id=author_id,
            priority="urgent"
        )

        assert announcement["site_id"] == str(site_id)
        assert announcement["title"] == "Important Announcement"
        assert announcement["author_id"] == str(author_id)
        assert announcement["priority"] == "urgent"
        assert announcement["is_pinned"] is True

    def test_get_course_announcements(self, website_service):
        """Test getting course announcements."""
        course_id = uuid4()

        # Create a website and some announcements
        site = website_service.create_course_website(
            course_id=course_id,
            title="Test Course",
            description="Test",
            instructor_id=uuid4()
        )

        for i in range(2):
            website_service.create_announcement(
                site_id=site["id"],
                title=f"Announcement {i}",
                content=f"Content {i}",
                author_id=uuid4()
            )

        announcements = website_service.get_course_announcements(course_id)

        assert isinstance(announcements, list)
        assert len(announcements) >= 2

    def test_generate_course_calendar(self, website_service):
        """Test generating course calendar."""
        course_id = uuid4()

        events = [
            {"title": "Week 1", "date": "2024-01-15T09:00:00Z", "type": "lesson"},
            {"title": "Assignment 1", "date": "2024-01-22T23:59:59Z", "type": "deadline"}
        ]

        calendar = website_service.generate_course_calendar(course_id)

        assert isinstance(calendar, list)
        assert len(calendar) >= 2

    def test_get_available_themes(self, website_service):
        """Test getting available themes."""
        themes = website_service.get_available_themes()

        assert isinstance(themes, dict)
        assert "default" in themes
        assert "academic" in themes
        assert "modern" in themes

    def test_customize_theme(self, website_service):
        """Test customizing website theme."""
        site_id = uuid4()

        customizations = {
            "colors": {"primary": "#ff0000"},
            "fonts": {"heading": "Arial"}
        }

        result = website_service.customize_theme(site_id, customizations)

        assert "colors" in result
        assert result["colors"]["primary"] == "#ff0000"

    def test_generate_seo_metadata(self, website_service):
        """Test generating SEO metadata."""
        site_id = uuid4()

        # Create site first
        website_service.create_course_website(
            course_id=uuid4(),
            title="Test Course",
            description="Test Description",
            instructor_id=uuid4()
        )

        seo = website_service.generate_seo_metadata(site_id)

        assert "title" in seo
        assert "description" in seo
        assert "keywords" in seo

    def test_get_accessibility_features(self, website_service):
        """Test getting accessibility features."""
        site_id = uuid4()

        features = website_service.get_accessibility_features(site_id)

        assert isinstance(features, dict)
        assert "screen_reader_support" in features
        assert "keyboard_navigation" in features



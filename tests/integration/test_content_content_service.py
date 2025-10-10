"""Tests for Content Service."""

import pytest
from uuid import uuid4

from curriculum.core.content import ContentStatus, ContentFormat, ContentType


@pytest.mark.unit
class TestContentService:
    """Tests for ContentService."""

    def test_create_content(self, content_service):
        """Test creating content."""
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
            description="Introduction to Python",
        )

        assert content is not None
        assert content.title == "Python Basics"
        assert content.author_id == author_id
        assert content.status == ContentStatus.DRAFT

    def test_get_content(self, content_service):
        """Test retrieving content."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
            description="Introduction to Python",
        )
        assert content is not None
        
        # Retrieve it
        retrieved = content_service.get_content(content.id)

        assert retrieved is not None
        assert retrieved.id == content.id
        assert retrieved.title == "Python Basics"

    def test_update_content(self, content_service):
        """Test updating content."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        
        # Update it
        updated = content_service.update_content(
            content.id,
            title="Updated Title",
            description="Updated description",
        )

        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == "Updated description"

    def test_delete_content(self, content_service):
        """Test soft deleting content."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        
        # Delete it
        result = content_service.delete_content(content.id)

        assert result is True
        retrieved = content_service.get_content(content.id)
        assert retrieved.is_deleted is True

    def test_publish_content(self, content_service):
        """Test publishing content."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        assert content.status == ContentStatus.DRAFT
        
        # Go through proper workflow: DRAFT -> INTERNAL_REVIEW -> EXTERNAL_REVIEW -> APPROVED
        content.transition_to(ContentStatus.INTERNAL_REVIEW)
        assert content.status == ContentStatus.INTERNAL_REVIEW
        
        content.transition_to(ContentStatus.EXTERNAL_REVIEW)
        assert content.status == ContentStatus.EXTERNAL_REVIEW
        
        content.transition_to(ContentStatus.APPROVED)
        assert content.status == ContentStatus.APPROVED

        # Now publish it
        published = content_service.publish_content(content.id)

        assert published is not None
        assert published.status == ContentStatus.PUBLISHED

    def test_list_content(self, content_service, sample_instructor):
        """Test listing content with pagination."""
        # Create multiple content items
        for i in range(5):
            content_service.create_content(
                title=f"Content {i}",
                content_type=ContentType.LESSON,
                format=ContentFormat.MARKDOWN,
                author_id=sample_instructor.id,
            )

        paged = content_service.list_content(page=1, page_size=3)

        assert paged.total >= 5
        assert len(paged.items) <= 3
        assert paged.page == 1

    def test_search_content(self, content_service):
        """Test searching content."""
        # Create content with searchable title
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics Tutorial",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
            description="Introduction to Python programming",
        )
        assert content is not None
        
        # Search for it
        results = content_service.search_content("Python")

        assert len(results) > 0
        assert any(c.id == content.id for c in results)

    def test_add_tag(self, content_service):
        """Test adding tags to content."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        
        # Add tag
        updated = content_service.add_tag(content.id, "python")

        assert updated is not None
        assert "python" in updated.tags

    def test_remove_tag(self, content_service):
        """Test removing tags from content."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        
        # Add then remove tag
        content_service.add_tag(content.id, "test")
        updated = content_service.remove_tag(content.id, "test")

        assert updated is not None
        assert "test" not in updated.tags

    def test_get_children(self, content_service, sample_instructor):
        """Test getting child content."""
        parent = content_service.create_content(
            title="Parent Course",
            content_type=ContentType.COURSE,
            format=ContentFormat.HTML,
            author_id=sample_instructor.id,
        )

        child1 = content_service.create_content(
            title="Child Lesson 1",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_instructor.id,
        )
        child1.parent_id = parent.id

        child2 = content_service.create_content(
            title="Child Lesson 2",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_instructor.id,
        )
        child2.parent_id = parent.id

        children = content_service.get_children(parent.id)

        assert len(children) == 2
        assert all(c.parent_id == parent.id for c in children)

    def test_increment_views(self, content_service):
        """Test incrementing view count."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        initial_views = content.view_count

        # Increment views
        content_service.increment_views(content.id)
        
        # Retrieve to check
        updated = content_service.get_content(content.id)
        assert updated.view_count == initial_views + 1

    def test_increment_downloads(self, content_service):
        """Test incrementing download count."""
        # Create content first
        author_id = uuid4()
        content = content_service.create_content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )
        assert content is not None
        initial_downloads = content.download_count

        # Increment downloads
        content_service.increment_downloads(content.id)
        
        # Retrieve to check
        updated = content_service.get_content(content.id)
        assert updated.download_count == initial_downloads + 1

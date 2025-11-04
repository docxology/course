"""Metadata management service."""

from typing import List, Optional
from uuid import UUID

from curriculum.core.metadata import (
    DublinCore,
    LRMIMetadata,
    Metadata,
    ResourceType,
    Tag,
    Taxonomy,
)


class MetadataService:
    """Service for managing content metadata."""

    def __init__(self) -> None:
        """Initialize metadata service."""
        self._metadata: dict[UUID, Metadata] = {}
        self._tags: dict[UUID, Tag] = {}
        self._tag_name_index: dict[str, UUID] = {}
        self._taxonomies: dict[UUID, Taxonomy] = {}

    def create_metadata(
        self,
        content_id: UUID,
        title: str,
        description: Optional[str] = None,
        resource_type: ResourceType = ResourceType.TEXT,
    ) -> Metadata:
        """Create metadata for content.

        Args:
            content_id: UUID of the content to create metadata for
            title: Metadata title
            description: Optional description
            resource_type: Type of resource (defaults to TEXT)

        Returns:
            Created Metadata instance
        """
        dublin_core = DublinCore(
            title=title,
            description=description,
            type=resource_type,
        )

        metadata = Metadata(content_id=content_id, dublin_core=dublin_core)
        self._metadata[metadata.id] = metadata
        return metadata

    def get_metadata(self, metadata_id: UUID) -> Optional[Metadata]:
        """Get metadata by ID.

        Args:
            metadata_id: UUID of the metadata to retrieve

        Returns:
            Metadata instance if found, None otherwise
        """
        return self._metadata.get(metadata_id)

    def get_metadata_by_content(self, content_id: UUID) -> Optional[Metadata]:
        """Get metadata for specific content.

        Args:
            content_id: UUID of the content

        Returns:
            Metadata instance if found, None otherwise
        """
        for metadata in self._metadata.values():
            if metadata.content_id == content_id:
                return metadata
        return None

    def update_dublin_core(
        self,
        metadata_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        creators: Optional[List[str]] = None,
        subjects: Optional[List[str]] = None,
    ) -> Optional[Metadata]:
        """Update Dublin Core metadata.

        Args:
            metadata_id: UUID of the metadata to update
            title: Optional new title
            description: Optional new description
            creators: Optional list of creators
            subjects: Optional list of subjects

        Returns:
            Updated Metadata instance if found, None otherwise
        """
        metadata = self.get_metadata(metadata_id)
        if not metadata:
            return None

        if title is not None:
            metadata.dublin_core.title = title
        if description is not None:
            metadata.dublin_core.description = description
        if creators is not None:
            metadata.dublin_core.creator = creators
        if subjects is not None:
            metadata.dublin_core.subject = subjects

        metadata.update_timestamp()
        return metadata

    def add_lrmi_metadata(
        self,
        metadata_id: UUID,
        educational_use: Optional[List[str]] = None,
        learning_resource_type: Optional[List[str]] = None,
        time_required: Optional[int] = None,
    ) -> Optional[Metadata]:
        """Add or update LRMI metadata.

        Args:
            metadata_id: UUID of the metadata to update
            educational_use: Optional list of educational use cases
            learning_resource_type: Optional list of learning resource types
            time_required: Optional time required in minutes

        Returns:
            Updated Metadata instance if found, None otherwise
        """
        metadata = self.get_metadata(metadata_id)
        if not metadata:
            return None

        if not metadata.lrmi:
            metadata.lrmi = LRMIMetadata()

        if educational_use is not None:
            metadata.lrmi.educational_use = educational_use
        if learning_resource_type is not None:
            metadata.lrmi.learning_resource_type = learning_resource_type
        if time_required is not None:
            metadata.lrmi.time_required = time_required

        metadata.update_timestamp()
        return metadata

    def add_custom_field(
        self, metadata_id: UUID, field_name: str, field_value: str
    ) -> Optional[Metadata]:
        """Add custom metadata field.

        Args:
            metadata_id: UUID of the metadata
            field_name: Name of the custom field
            field_value: Value for the custom field

        Returns:
            Updated Metadata instance if found, None otherwise
        """
        metadata = self.get_metadata(metadata_id)
        if not metadata:
            return None

        metadata.custom_fields[field_name] = field_value
        metadata.update_timestamp()
        return metadata

    def create_or_get_tag(self, tag_name: str) -> Tag:
        """Create a new tag or get existing one.

        Args:
            tag_name: Name of the tag

        Returns:
            Tag instance (created or existing)
        """
        slug = tag_name.lower().replace(" ", "-")

        # Check if tag exists
        if slug in self._tag_name_index:
            tag_id = self._tag_name_index[slug]
            return self._tags[tag_id]

        # Create new tag
        tag = Tag(name=tag_name, slug=slug)
        self._tags[tag.id] = tag
        self._tag_name_index[slug] = tag.id
        return tag

    def get_tag(self, tag_id: UUID) -> Optional[Tag]:
        """Get tag by ID.

        Args:
            tag_id: UUID of the tag

        Returns:
            Tag instance if found, None otherwise
        """
        return self._tags.get(tag_id)

    def get_tag_by_name(self, tag_name: str) -> Optional[Tag]:
        """Get tag by name.

        Args:
            tag_name: Name of the tag

        Returns:
            Tag instance if found, None otherwise
        """
        slug = tag_name.lower().replace(" ", "-")
        tag_id = self._tag_name_index.get(slug)
        return self._tags.get(tag_id) if tag_id else None

    def increment_tag_usage(self, tag_name: str) -> Optional[Tag]:
        """Increment tag usage count.

        Args:
            tag_name: Name of the tag

        Returns:
            Updated Tag instance
        """
        tag = self.create_or_get_tag(tag_name)
        tag.increment_usage()
        return tag

    def create_taxonomy(
        self,
        name: str,
        path: str,
        parent_id: Optional[UUID] = None,
        level: int = 0,
    ) -> Taxonomy:
        """Create a taxonomy category.

        Args:
            name: Taxonomy name
            path: Taxonomy path
            parent_id: Optional parent taxonomy ID
            level: Taxonomy level (defaults to 0)

        Returns:
            Created Taxonomy instance
        """
        taxonomy = Taxonomy(
            name=name,
            path=path,
            parent_id=parent_id,
            level=level,
        )
        self._taxonomies[taxonomy.id] = taxonomy
        return taxonomy

    def get_taxonomy(self, taxonomy_id: UUID) -> Optional[Taxonomy]:
        """Get taxonomy by ID.

        Args:
            taxonomy_id: UUID of the taxonomy

        Returns:
            Taxonomy instance if found, None otherwise
        """
        return self._taxonomies.get(taxonomy_id)

    def get_taxonomy_children(self, parent_id: UUID) -> List[Taxonomy]:
        """Get child taxonomies.

        Args:
            parent_id: UUID of the parent taxonomy

        Returns:
            List of child Taxonomy instances
        """
        return [tax for tax in self._taxonomies.values() if tax.parent_id == parent_id]

    def get_all_tags(self) -> List[Tag]:
        """Get all tags.

        Returns:
            List of all Tag instances
        """
        return list(self._tags.values())

    def get_popular_tags(self, limit: int = 10) -> List[Tag]:
        """Get most popular tags by usage count.

        Args:
            limit: Maximum number of tags to return (defaults to 10)

        Returns:
            List of most popular Tag instances, sorted by usage count
        """
        tags = sorted(self._tags.values(), key=lambda t: t.usage_count, reverse=True)
        return tags[:limit]

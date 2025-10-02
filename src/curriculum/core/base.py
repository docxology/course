"""Base models and mixins for the Curriculum Repository System."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class UUIDMixin(BaseModel):
    """Mixin for UUID primary key."""

    id: UUID = Field(default_factory=uuid4)


class SoftDeleteMixin(BaseModel):
    """Mixin for soft delete functionality."""

    deleted_at: Optional[datetime] = None
    is_deleted: bool = False

    def soft_delete(self) -> None:
        """Mark the record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class BaseEntity(UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Base entity with common fields."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class PagedResponse(BaseModel):
    """Paged response wrapper."""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: list, total: int, page: int, page_size: int) -> "PagedResponse":
        """Create a paged response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

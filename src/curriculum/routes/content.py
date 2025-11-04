"""Content API routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel

from curriculum.content.content import ContentService
from curriculum.content.rendering import RenderingService
from curriculum.content.version_control import VersionControlService
from curriculum.core.base import PagedResponse
from curriculum.core.content import Content, ContentFormat, ContentStatus, ContentType

router = APIRouter()

# Service instances (in production, these would be injected via dependency injection)
content_service = ContentService()
rendering_service = RenderingService()
version_service = VersionControlService()


# Request/Response models
class CreateContentRequest(BaseModel):
    """Request model for creating content."""

    title: str
    description: Optional[str] = None
    content_type: ContentType
    format: ContentFormat
    content_body: Optional[str] = None
    tags: List[str] = []
    parent_id: Optional[UUID] = None


class UpdateContentRequest(BaseModel):
    """Request model for updating content."""

    title: Optional[str] = None
    description: Optional[str] = None
    content_body: Optional[str] = None
    tags: Optional[List[str]] = None


class ContentResponse(BaseModel):
    """Response model for content."""

    id: str
    title: str
    description: Optional[str] = None
    content_type: str
    format: str
    status: str
    author_id: str
    created_at: str
    updated_at: str
    tags: List[str]
    view_count: int
    download_count: int


# Routes
@router.post("/", response_model=ContentResponse)
async def create_content(request: CreateContentRequest):
    """Create new content."""
    content = content_service.create_content(
        title=request.title,
        content_type=request.content_type,
        format=request.format,
        author_id=UUID("12345678-1234-5678-1234-567812345678"),  # TODO: Get from auth
        description=request.description,
        content_body=request.content_body,
    )

    if not content:
        raise HTTPException(status_code=400, detail="Failed to create content")

    # Add tags
    for tag in request.tags:
        content_service.add_tag(content.id, tag)

    return _content_to_response(content)


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: UUID = Path(..., description="Content ID")):
    """Get content by ID."""
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Increment view count
    content_service.increment_views(content_id)

    return _content_to_response(content)


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    request: UpdateContentRequest,
    content_id_path: UUID = Path(..., description="Content ID"),
):
    """Update content."""
    if content_id != content_id_path:
        raise HTTPException(status_code=400, detail="Content ID mismatch")

    content = content_service.update_content(
        content_id,
        title=request.title,
        description=request.description,
        content_body=request.content_body,
    )

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Update tags if provided
    if request.tags is not None:
        # Clear existing tags and add new ones
        for tag in content.tags:
            content_service.remove_tag(content_id, tag)
        for tag in request.tags:
            content_service.add_tag(content_id, tag)

    return _content_to_response(content)


@router.delete("/{content_id}")
async def delete_content(content_id: UUID):
    """Soft delete content."""
    success = content_service.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"message": "Content deleted successfully"}


@router.post("/{content_id}/publish")
async def publish_content(content_id: UUID):
    """Publish content."""
    content = content_service.publish_content(content_id)
    if not content:
        raise HTTPException(
            status_code=400, detail="Cannot publish content. Content must be approved first."
        )

    return {"message": "Content published successfully", "status": content.status}


@router.post("/{content_id}/status/{new_status}")
async def change_content_status(
    content_id: UUID,
    new_status: ContentStatus,
    content_id_path: UUID = Path(..., description="Content ID"),
):
    """Change content status."""
    if content_id != content_id_path:
        raise HTTPException(status_code=400, detail="Content ID mismatch")

    content = content_service.transition_status(content_id, new_status)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return {"message": f"Content status changed to {new_status}", "status": content.status}


@router.get("/", response_model=dict)
async def list_content(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ContentStatus] = Query(None, description="Filter by status"),
    author_id: Optional[UUID] = Query(None, description="Filter by author"),
    search: Optional[str] = Query(None, description="Search query"),
):
    """List content with pagination and filtering."""
    if search:
        contents = content_service.search_content(search)
        return {
            "items": [_content_to_response(c) for c in contents[:page_size]],
            "total": len(contents),
            "page": 1,
            "page_size": page_size,
        }

    paged_response = content_service.list_content(
        page=page,
        page_size=page_size,
        status=status,
        author_id=author_id,
    )

    return {
        "items": [_content_to_response(c) for c in paged_response.items],
        "total": paged_response.total,
        "page": paged_response.page,
        "page_size": paged_response.page_size,
        "total_pages": paged_response.total_pages,
    }


@router.get("/{content_id}/render")
async def render_content(
    content_id: UUID,
    format: str = Query("html", description="Target format"),
):
    """Render content in specified format."""
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    result = rendering_service.render_content(content, format)
    return result


@router.post("/{content_id}/download")
async def download_content(content_id: UUID):
    """Download content (increment download count)."""
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content_service.increment_downloads(content_id)

    return {
        "message": "Download count incremented",
        "download_count": content.download_count,
    }


@router.get("/{content_id}/versions")
async def get_content_versions(content_id: UUID):
    """Get all versions of content."""
    versions = version_service.get_content_versions(content_id)

    return {
        "content_id": str(content_id),
        "versions": [
            {
                "id": str(v.id),
                "version": v.version,
                "title": v.title,
                "committed_at": v.committed_at,
                "author_id": str(v.author_id),
            }
            for v in versions
        ],
    }


@router.get("/{content_id}/children")
async def get_content_children(content_id: UUID):
    """Get child content items."""
    children = content_service.get_children(content_id)

    return {
        "parent_id": str(content_id),
        "children": [_content_to_response(c) for c in children],
    }


# Helper functions
def _content_to_response(content: Content) -> ContentResponse:
    """Convert Content model to response model."""
    return ContentResponse(
        id=str(content.id),
        title=content.title,
        description=content.description,
        content_type=content.content_type,
        format=content.format,
        status=content.status,
        author_id=str(content.author_id),
        created_at=content.created_at.isoformat(),
        updated_at=content.updated_at.isoformat(),
        tags=content.tags,
        view_count=content.view_count,
        download_count=content.download_count,
    )

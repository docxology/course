"""Search service using Elasticsearch."""

from typing import List, Dict, Any, Optional
from uuid import UUID

from curriculum.core.content import Content
from curriculum.config import settings


class SearchService:
    """Service for searching content using Elasticsearch."""

    def __init__(self) -> None:
        """Initialize search service."""
        self._index_name = settings.elasticsearch_index
        self._client = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to Elasticsearch."""
        try:
            from elasticsearch import AsyncElasticsearch

            self._client = AsyncElasticsearch([settings.elasticsearch_url])
            # Test connection
            await self._client.info()
            self._connected = True

            # Create index if it doesn't exist
            await self._ensure_index_exists()

        except Exception as e:
            print(f"Failed to connect to Elasticsearch: {e}")
            self._connected = False

    async def disconnect(self) -> None:
        """Disconnect from Elasticsearch."""
        if self._client:
            await self._client.close()

    def is_connected(self) -> bool:
        """Check if connected to Elasticsearch."""
        return self._connected

    async def index_content(self, content: Content) -> bool:
        """Index content for search."""
        if not self._connected or not self._client:
            return False

        document = {
            "id": str(content.id),
            "title": content.title,
            "description": content.description,
            "content_body": content.content_body,
            "content_type": content.content_type.value,
            "format": content.format.value,
            "status": content.status.value,
            "author_id": str(content.author_id),
            "tags": content.tags,
            "keywords": content.keywords,
            "created_at": content.created_at.isoformat(),
            "updated_at": content.updated_at.isoformat(),
            "view_count": content.view_count,
            "is_deleted": content.is_deleted,
        }

        try:
            await self._client.index(
                index=self._index_name,
                id=str(content.id),
                document=document,
                refresh=True,  # Make immediately available for search
            )
            return True
        except Exception as e:
            print(f"Failed to index content {content.id}: {e}")
            return False

    async def delete_from_index(self, content_id: UUID) -> bool:
        """Remove content from search index."""
        if not self._connected or not self._client:
            return False

        try:
            await self._client.delete(
                index=self._index_name,
                id=str(content_id),
                refresh=True,
            )
            return True
        except Exception:
            return False

    async def search(
        self,
        query: str,
        content_type: Optional[str] = None,
        author_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search for content."""
        if not self._connected or not self._client:
            return {"total": 0, "results": [], "error": "Search service not available"}

        # Build Elasticsearch query
        es_query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^3", "description^2", "content_body", "tags", "keywords"],
                            "type": "best_fields",
                        }
                    }
                ],
                "filter": [],
            }
        }

        # Add filters
        if content_type:
            es_query["bool"]["filter"].append({
                "term": {"content_type": content_type}
            })

        if author_id:
            es_query["bool"]["filter"].append({
                "term": {"author_id": str(author_id)}
            })

        if tags:
            es_query["bool"]["filter"].append({
                "terms": {"tags": tags}
            })

        # Exclude deleted content
        es_query["bool"]["filter"].append({
            "term": {"is_deleted": False}
        })

        try:
            # Execute search
            response = await self._client.search(
                index=self._index_name,
                query=es_query,
                size=limit,
                from_=offset,
                sort=[
                    {"_score": {"order": "desc"}},
                    {"updated_at": {"order": "desc"}},
                ],
            )

            # Process results
            hits = response["hits"]
            results = []

            for hit in hits["hits"]:
                source = hit["_source"]
                results.append({
                    "id": source["id"],
                    "title": source["title"],
                    "description": source["description"],
                    "content_type": source["content_type"],
                    "author_id": source["author_id"],
                    "tags": source["tags"],
                    "score": hit["_score"],
                    "highlight": hit.get("highlight", {}),
                })

            return {
                "total": hits["total"]["value"],
                "results": results,
                "max_score": hits["max_score"],
            }

        except Exception as e:
            return {"total": 0, "results": [], "error": str(e)}

    async def suggest(self, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions."""
        if not self._connected or not self._client:
            return []

        try:
            response = await self._client.search(
                index=self._index_name,
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "tags"],
                        "type": "phrase_prefix",
                    }
                },
                size=limit,
                _source=["title", "tags"],
            )

            suggestions = []
            seen_titles = set()

            for hit in response["hits"]["hits"]:
                source = hit["_source"]

                # Add title if not already seen
                if source["title"] not in seen_titles:
                    suggestions.append(source["title"])
                    seen_titles.add(source["title"])

                # Add unique tags
                for tag in source["tags"]:
                    if tag not in seen_titles and len(suggestions) < limit:
                        suggestions.append(tag)
                        seen_titles.add(tag)

            return suggestions[:limit]

        except Exception:
            return []

    async def get_similar_content(
        self,
        content_id: UUID,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find similar content using more-like-this query."""
        if not self._connected or not self._client:
            return []

        try:
            response = await self._client.search(
                index=self._index_name,
                query={
                    "more_like_this": {
                        "fields": ["title", "description", "content_body", "tags"],
                        "like": [{"_index": self._index_name, "_id": str(content_id)}],
                        "min_term_freq": 1,
                        "max_query_terms": 12,
                    }
                },
                size=limit,
                _source=["id", "title", "description", "content_type", "tags"],
            )

            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                results.append({
                    "id": source["id"],
                    "title": source["title"],
                    "description": source["description"],
                    "content_type": source["content_type"],
                    "tags": source["tags"],
                    "score": hit["_score"],
                })

            return results

        except Exception:
            return []

    async def _ensure_index_exists(self) -> None:
        """Ensure search index exists with proper mapping."""
        if not self._client:
            return

        # Check if index exists
        if await self._client.indices.exists(index=self._index_name):
            return

        # Create index with mapping
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "description": {"type": "text", "analyzer": "standard"},
                    "content_body": {"type": "text", "analyzer": "standard"},
                    "content_type": {"type": "keyword"},
                    "format": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "author_id": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "keywords": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "view_count": {"type": "integer"},
                    "is_deleted": {"type": "boolean"},
                }
            }
        }

        await self._client.indices.create(index=self._index_name, body=mapping)

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get search index statistics."""
        if not self._connected or not self._client:
            return {"error": "Search service not available"}

        try:
            stats = await self._client.indices.stats(index=self._index_name)
            return {
                "index_name": self._index_name,
                "total_docs": stats["indices"][self._index_name]["total"]["docs"]["count"],
                "size_in_bytes": stats["indices"][self._index_name]["total"]["store"]["size_in_bytes"],
                "health": "green",  # Would check cluster health in production
            }
        except Exception as e:
            return {"error": str(e)}

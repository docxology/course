# Module: search.search

**File:** `src/curriculum/search/search.py`

## Description

Search service using Elasticsearch.

## Classes

### `SearchService`

Service for searching content using Elasticsearch.

**Methods:** 10


**Method List:**

- `__init__`: Initialize search service.

- `connect`: Connect to Elasticsearch.

- `disconnect`: Disconnect from Elasticsearch.

- `index_content`: Index content for search.

- `delete_from_index`: Remove content from search index.

- `search`: Search for content.

- `suggest`: Get search suggestions.

- `get_similar_content`: Find similar content using more-like-this query.

- `_ensure_index_exists`: Ensure search index exists with proper mapping.

- `get_index_stats`: Get search index statistics.

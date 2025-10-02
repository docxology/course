# Search Module

The search module provides powerful search and discovery capabilities.

## Services

- `SearchService`: Elasticsearch-based search
- `VisualizationService`: Interactive charts and graphs
- `WebsiteService`: Course website generation

## Features

- Full-text search with relevance scoring
- Content indexing and discovery
- Interactive visualizations
- Course website generation
- SEO optimization
- Search suggestions

## Usage

```python
from curriculum.search import SearchService, VisualizationService

search = SearchService()
visualization = VisualizationService()

# Search content
results = await search.search("python programming", limit=10)

# Create visualization
chart = visualization.create_progress_chart(
    content_id=content_id,
    user_id=user_id,
    progress_data={"dates": ["2024-01-01"], "scores": [85]},
)
```

## Testing

```bash
pytest tests/test_search/
```


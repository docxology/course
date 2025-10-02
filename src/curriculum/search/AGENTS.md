# AI Agents Guide - Search Module

## Overview

The search module provides powerful search and discovery capabilities for the curriculum system.

## Module Structure

```
search/
├── search.py       # Elasticsearch-based search
├── visualization.py # Interactive charts and graphs
├── website.py      # Course website generation
└── README.md       # Module documentation
```

## Development Guidelines

### When Working on Search Features

1. **Use Elasticsearch effectively**:
```python
async def search(self, query: str, content_type: Optional[str] = None):
    es_query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description^2", "content_body"],
                    }
                }
            ],
            "filter": [],
        }
    }

    if content_type:
        es_query["bool"]["filter"].append({"term": {"content_type": content_type}})

    response = await self._client.search(index=self._index_name, query=es_query)
    return self._process_search_results(response)
```

2. **Implement proper indexing**:
```python
async def index_content(self, content: Content) -> bool:
    document = {
        "id": str(content.id),
        "title": content.title,
        "description": content.description,
        "content_body": content.content_body,
        "content_type": content.content_type.value,
        "author_id": str(content.author_id),
        "tags": content.tags,
        "created_at": content.created_at.isoformat(),
    }

    await self._client.index(
        index=self._index_name,
        id=str(content.id),
        document=document,
        refresh=True,
    )
    return True
```

3. **Add search suggestions**:
```python
async def suggest(self, query: str, limit: int = 10) -> List[str]:
    response = await self._client.search(
        index=self._index_name,
        query={"multi_match": {"query": query, "type": "phrase_prefix"}},
        size=limit,
        _source=["title", "tags"],
    )

    suggestions = []
    for hit in response["hits"]["hits"]:
        suggestions.extend(hit["_source"]["tags"])

    return list(set(suggestions))[:limit]
```

### Visualization Features

1. **Create interactive charts**:
```python
def create_progress_chart(self, content_id: UUID, user_id: UUID, progress_data):
    return self.create_visualization(
        content_id=content_id,
        title="Learning Progress",
        visualization_type="line_chart",
        data={
            "labels": progress_data["dates"],
            "datasets": [{"label": "Progress", "data": progress_data["scores"]}],
        },
    )
```

2. **Support multiple chart types**:
```python
def get_visualization_types(self) -> List[str]:
    return [
        "bar_chart", "line_chart", "pie_chart",
        "scatter_plot", "heatmap", "network_graph",
    ]
```

### Website Generation

1. **Create course websites**:
```python
def create_course_website(self, course_id: UUID, title: str, description: str):
    return {
        "id": str(uuid4()),
        "course_id": str(course_id),
        "title": title,
        "domain": f"{title.lower().replace(' ', '-')}.learn.edu",
        "theme": "default",
        "features": ["student_dashboard", "instructor_dashboard"],
    }
```

2. **Generate SEO metadata**:
```python
def generate_seo_metadata(self, site_id: UUID) -> Dict[str, Any]:
    site = self.get_site(site_id)
    return {
        "title": site["title"],
        "description": site["description"],
        "keywords": ["education", "course", "learning"],
        "og_title": site["title"],
        "og_image": "/images/course-default.png",
    }
```

### Testing Requirements

- **Test search functionality**
- **Test visualization creation**
- **Test website generation**
- **Test indexing operations**

Example test:
```python
def test_search_functionality():
    # Index content
    await search_service.index_content(content)

    # Search content
    results = await search_service.search("python programming")

    assert len(results["results"]) > 0
    assert results["total"] >= 1
```

### Performance Considerations

- **Optimize search queries** for speed
- **Implement proper indexing** strategies
- **Cache frequently accessed data**
- **Use async processing** for heavy operations

### Common Patterns

#### Search Query Building
```python
def _build_search_query(self, query: str, filters: Dict[str, Any]):
    es_query = {"bool": {"must": [], "filter": []}}

    # Add text search
    es_query["bool"]["must"].append({
        "multi_match": {
            "query": query,
            "fields": ["title^3", "description^2", "content_body"],
        }
    })

    # Add filters
    for field, value in filters.items():
        es_query["bool"]["filter"].append({"term": {field: value}})

    return es_query
```

#### Visualization Data
```python
def create_visualization(self, content_id: UUID, title: str, viz_type: str, data: Dict):
    return {
        "id": str(uuid4()),
        "content_id": str(content_id),
        "title": title,
        "type": viz_type,
        "data": data,
        "is_interactive": True,
    }
```

### Extension Points

- Custom search algorithms
- Advanced visualization types
- Website customization
- Search result ranking
- Content recommendation engines


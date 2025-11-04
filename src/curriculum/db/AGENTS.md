# AI Agents Guide - Database Module

## Overview

The database module provides a unified abstraction layer for multiple database systems, enabling seamless switching between different storage backends while maintaining consistent APIs across the application.

## Module Structure

```
db/
├── base.py         # Abstract database interface and manager
├── mongodb.py      # MongoDB document database adapter
├── postgresql.py   # PostgreSQL relational database adapter
├── __init__.py     # Module exports
├── README.md       # Module documentation
└── AGENTS.md       # This file
```

## Database Interface Design

### Abstract Base Class

All database adapters inherit from `DatabaseInterface`:

```python
class DatabaseInterface(ABC):
    @abstractmethod
    async def connect(self) -> None: pass
    @abstractmethod
    async def disconnect(self) -> None: pass
    @abstractmethod
    async def create(self, entity: T) -> T: pass
    @abstractmethod
    async def get(self, entity_id: UUID, entity_type: Type[T]) -> Optional[T]: pass
    @abstractmethod
    async def update(self, entity: T) -> T: pass
    @abstractmethod
    async def delete(self, entity_id: UUID, entity_type: Type[T]) -> bool: pass
    @abstractmethod
    async def list(self, entity_type: Type[T], filters: Optional[Dict] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]: pass
    @abstractmethod
    async def count(self, entity_type: Type[T], filters: Optional[Dict] = None) -> int: pass
```

### Database Manager

The `DatabaseManager` coordinates multiple database connections:

```python
db_manager = DatabaseManager()

# Register databases
db_manager.register_database("mongodb", mongo_adapter, default=True)
db_manager.register_database("postgres", postgres_adapter)

# Initialize all connections
await db_manager.initialize_all()

# Get specific database
mongo_db = db_manager.get_database("mongodb")
```

## Implementation Guidelines

### MongoDB Adapter

1. **Document Storage Strategy**:
```python
class MongoDBAdapter(DatabaseInterface):
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.mongodb_database]

    async def create(self, entity: BaseEntity) -> BaseEntity:
        collection = self._get_collection(entity.__class__)
        entity_dict = entity.model_dump()
        result = await collection.insert_one(entity_dict)
        entity.id = result.inserted_id
        return entity
```

2. **Collection Mapping**:
```python
def _get_collection(self, entity_type: Type) -> AsyncIOMotorCollection:
    mapping = {
        Content: "contents",
        User: "users",
        LearningEvent: "events",
    }
    collection_name = mapping.get(entity_type, entity_type.__name__.lower())
    return self.db[collection_name]
```

3. **Indexing Strategy**:
```python
async def _ensure_indexes(self) -> None:
    # Content search indexes
    await self.db.contents.create_index([
        ("title", "text"),
        ("description", "text"),
        ("tags", "text")
    ])

    # User lookup indexes
    await self.db.users.create_index([("email", 1)], unique=True)
    await self.db.users.create_index([("username", 1)], unique=True)
```

### PostgreSQL Adapter

1. **Relational Mapping**:
```python
class PostgreSQLAdapter(DatabaseInterface):
    def __init__(self):
        self.engine = create_async_engine(settings.postgresql_url)
        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession)

    async def create(self, entity: BaseEntity) -> BaseEntity:
        async with self.session_factory() as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity
```

2. **SQLAlchemy Models**:
```python
class ContentModel(Base):
    __tablename__ = "contents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(500), nullable=False)
    content_body = Column(Text)
    status = Column(String(50), default="draft")
    author_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Development Patterns

### Connection Management

1. **Health Checks**:
```python
async def health_check(self) -> Dict[str, Any]:
    try:
        # Ping database
        await self._ping()
        return {"status": "healthy", "database": self.database_name}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

2. **Connection Pooling**:
```python
# MongoDB connection pool
self.client = AsyncIOMotorClient(
    settings.mongodb_url,
    maxPoolSize=20,
    minPoolSize=5,
    maxIdleTimeMS=30000
)

# PostgreSQL connection pool
self.engine = create_async_engine(
    settings.postgresql_url,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### Error Handling

1. **Database-Specific Errors**:
```python
async def create(self, entity: BaseEntity) -> BaseEntity:
    try:
        return await self._create_entity(entity)
    except DuplicateKeyError:
        raise EntityAlreadyExistsError(f"Entity {entity.id} already exists")
    except ConnectionError:
        raise DatabaseConnectionError("Database connection failed")
    except Exception as e:
        raise DatabaseError(f"Database operation failed: {str(e)}")
```

2. **Transaction Management**:
```python
async def atomic_update(self, entity_id: UUID, updates: Dict) -> Optional[BaseEntity]:
    async with self.session_factory() as session:
        try:
            entity = await session.get(EntityModel, entity_id)
            if not entity:
                return None

            # Apply updates
            for field, value in updates.items():
                setattr(entity, field, value)

            await session.commit()
            await session.refresh(entity)
            return self._model_to_entity(entity)
        except Exception:
            await session.rollback()
            raise
```

## Testing Guidelines

### Database Adapter Tests

1. **Mock Database Connections**:
```python
@pytest.fixture
def mock_mongo_adapter():
    adapter = MongoDBAdapter()
    adapter.client = Mock()
    adapter.db = Mock()
    return adapter
```

2. **Test Data Isolation**:
```python
class TestMongoDBAdapter:
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        # Use test database
        self.adapter.db = self.adapter.client.test_db
        yield
        # Cleanup test data
        self.adapter.client.drop_database("test_db")
```

3. **Async Test Patterns**:
```python
async def test_create_content(self, mongo_adapter, sample_content):
    result = await mongo_adapter.create(sample_content)

    assert result.id is not None
    assert result.title == sample_content.title

    # Verify persistence
    retrieved = await mongo_adapter.get(result.id, Content)
    assert retrieved is not None
```

### Integration Tests

1. **Real Database Tests**:
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_integration():
    # Test with real database connections
    adapter = MongoDBAdapter()
    await adapter.connect()

    try:
        # Perform operations
        content = await adapter.create(sample_content)
        assert content.id is not None
    finally:
        await adapter.disconnect()
```

2. **Performance Tests**:
```python
@pytest.mark.performance
async def test_bulk_operations(self, mongo_adapter):
    # Test bulk insert performance
    entities = [create_sample_entity(i) for i in range(1000)]

    start_time = time.time()
    results = await asyncio.gather(*[
        mongo_adapter.create(entity) for entity in entities
    ])
    end_time = time.time()

    assert len(results) == 1000
    assert end_time - start_time < 5.0  # Should complete in under 5 seconds
```

## Performance Considerations

### Query Optimization

1. **Indexing Strategy**:
```python
# Compound indexes for common queries
await self.db.contents.create_index([
    ("author_id", 1),
    ("status", 1),
    ("created_at", -1)
])

# Text indexes for search
await self.db.contents.create_index([
    ("$**", "text")
])
```

2. **Query Patterns**:
```python
# Efficient filtering
async def list_by_author_and_status(self, author_id: UUID, status: str) -> List[Content]:
    return await self.db.contents.find({
        "author_id": author_id,
        "status": status,
        "is_deleted": {"$ne": True}
    }).sort("created_at", -1).to_list(None)
```

### Connection Management

1. **Connection Reuse**:
```python
# Singleton pattern for database connections
class DatabaseManager:
    _instance = None

    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

2. **Connection Health Monitoring**:
```python
async def monitor_connections(self) -> None:
    while True:
        for db_name, adapter in self._databases.items():
            health = await adapter.health_check()
            if health["status"] != "healthy":
                logger.warning(f"Database {db_name} health check failed: {health}")
        await asyncio.sleep(30)  # Check every 30 seconds
```

## Security Considerations

### Data Sanitization

1. **Input Validation**:
```python
async def create(self, entity: BaseEntity) -> BaseEntity:
    # Validate entity before database insertion
    if not self._validate_entity(entity):
        raise ValidationError("Invalid entity data")

    return await self._create_entity(entity)
```

2. **SQL Injection Prevention**:
```python
# Use parameterized queries
async def get_by_field(self, field: str, value: Any) -> List[BaseEntity]:
    # Safe parameterized query
    query = text("SELECT * FROM entities WHERE :field = :value")
    result = await self.session.execute(query, {"field": field, "value": value})
    return [self._row_to_entity(row) for row in result]
```

### Access Control

1. **Row-Level Security**:
```python
async def list_content(self, user_id: UUID) -> List[Content]:
    # Only return content user has access to
    return await self.db.contents.find({
        "$or": [
            {"author_id": user_id},
            {"is_public": True},
            {"allowed_users": user_id}
        ],
        "is_deleted": {"$ne": True}
    }).to_list(None)
```

## Migration Strategy

### Schema Evolution

1. **Database Migrations**:
```python
# Alembic migration for PostgreSQL
class AddContentMetadata(Base):
    __tablename__ = "contents"

    id = Column(UUID, primary_key=True)
    metadata = Column(JSONB)  # Add new metadata column
```

2. **Data Transformation**:
```python
async def migrate_content_metadata(self) -> None:
    # Transform existing content to include metadata field
    contents = await self.db.contents.find({"metadata": {"$exists": False}}).to_list(None)

    for content in contents:
        content["metadata"] = self._extract_metadata(content)
        await self.db.contents.replace_one({"_id": content["_id"]}, content)
```

## Monitoring and Observability

### Metrics Collection

1. **Performance Metrics**:
```python
async def collect_metrics(self) -> Dict[str, Any]:
    return {
        "connection_pool_size": self.client._pool_size,
        "active_connections": len(self.client._pool._pool),
        "query_count": self._query_counter,
        "average_response_time": self._response_time_avg
    }
```

2. **Logging Strategy**:
```python
async def _log_query(self, query: str, duration: float, success: bool) -> None:
    log_data = {
        "query": query[:100],  # Truncate long queries
        "duration_ms": duration * 1000,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }

    if duration > 1.0:  # Log slow queries
        logger.warning(f"Slow query detected: {log_data}")
    else:
        logger.info(f"Query executed: {log_data}")
```

## Best Practices

### When to Use Each Database

**MongoDB** (Document Database):
- Content storage (flexible schema)
- User sessions and activity tracking
- Analytics events and logs
- Metadata and taxonomies

**PostgreSQL** (Relational Database):
- User authentication and authorization
- Assessment results and grades
- Structured reporting data
- Audit trails and compliance data

### Hybrid Approach

1. **Read/Write Splitting**:
```python
async def get_content_with_analytics(self, content_id: UUID) -> Dict[str, Any]:
    # Get content from MongoDB (fast, flexible)
    content = await self.mongodb_adapter.get(content_id, Content)

    # Get analytics from PostgreSQL (structured, reportable)
    analytics = await self.postgres_adapter.get_analytics(content_id)

    return {
        "content": content,
        "analytics": analytics
    }
```

2. **Event Sourcing**:
```python
async def track_user_action(self, user_id: UUID, action: str, metadata: Dict) -> None:
    # Store event in MongoDB for flexibility
    event = LearningEvent(
        user_id=user_id,
        verb=ActivityVerb(action),
        metadata=metadata
    )
    await self.mongodb_adapter.create(event)

    # Update aggregated stats in PostgreSQL
    await self.postgres_adapter.increment_user_stat(user_id, action)
```

### Consistency Patterns

1. **Eventual Consistency**:
```python
async def update_content_and_cache(self, content_id: UUID, updates: Dict) -> Content:
    # Update primary storage
    content = await self.mongodb_adapter.update(content_id, updates)

    # Invalidate cache asynchronously
    asyncio.create_task(self._invalidate_content_cache(content_id))

    return content
```

2. **Strong Consistency**:
```python
async def transfer_ownership(self, content_id: UUID, new_owner_id: UUID) -> bool:
    async with self.postgres_adapter.transaction() as session:
        # Update ownership in relational data
        await session.execute(
            "UPDATE content_permissions SET owner_id = :new_owner WHERE content_id = :content_id",
            {"new_owner": new_owner_id, "content_id": content_id}
        )

        # Update document metadata
        await self.mongodb_adapter.update_metadata(content_id, {"owner_id": new_owner_id})

        await session.commit()
        return True
```

## Common Issues and Solutions

### Connection Issues

1. **Connection Timeout**:
```python
async def handle_connection_timeout(self) -> None:
    try:
        await self.client.admin.command('ping')
    except ServerTimeoutError:
        logger.error("Database connection timeout")
        await self._reconnect()
```

2. **Connection Pool Exhaustion**:
```python
async def monitor_connection_pool(self) -> None:
    if self.client._pool_size > self.client._max_pool_size * 0.9:
        logger.warning("Connection pool nearly exhausted")
        # Scale up connections or implement queuing
```

### Data Consistency

1. **Duplicate Key Handling**:
```python
async def safe_create(self, entity: BaseEntity) -> Optional[BaseEntity]:
    try:
        return await self.create(entity)
    except DuplicateKeyError as e:
        # Try to retrieve existing entity
        existing = await self.get(entity.id, entity.__class__)
        if existing and existing.equals(entity):
            return existing
        raise e
```

2. **Race Condition Prevention**:
```python
async def atomic_increment(self, entity_id: UUID, field: str) -> bool:
    # Use atomic operations to prevent race conditions
    result = await self.db.entities.update_one(
        {"_id": entity_id},
        {"$inc": {field: 1}}
    )
    return result.modified_count > 0
```

## Extension Points

### Custom Database Adapters

1. **Redis Adapter**:
```python
class RedisAdapter(DatabaseInterface):
    def __init__(self):
        self.redis = redis.Redis.from_url(settings.redis_url)

    async def get(self, entity_id: UUID, entity_type: Type[T]) -> Optional[T]:
        key = f"{entity_type.__name__}:{entity_id}"
        data = self.redis.get(key)
        if data:
            return entity_type.model_validate_json(data)
        return None
```

2. **Elasticsearch Adapter**:
```python
class ElasticsearchAdapter(DatabaseInterface):
    def __init__(self):
        self.es = Elasticsearch(settings.elasticsearch_url)

    async def search_content(self, query: str, limit: int = 20) -> List[Content]:
        response = await self.es.search(
            index="contents",
            query={"multi_match": {"query": query, "fields": ["title", "content"]}},
            size=limit
        )
        return [Content(**hit["_source"]) for hit in response["hits"]["hits"]]
```

### Database Sharding

1. **Horizontal Partitioning**:
```python
def _get_shard_key(self, entity: BaseEntity) -> str:
    if isinstance(entity, Content):
        return entity.author_id.hex[:2]  # First 2 hex chars as shard key
    elif isinstance(entity, User):
        return entity.email[0].lower()  # First letter as shard key
    return "default"
```

2. **Shard Management**:
```python
async def migrate_to_shard(self, shard_key: str, entities: List[BaseEntity]) -> None:
    shard_db = self._get_shard_database(shard_key)

    for entity in entities:
        await shard_db.create(entity)
        await self._remove_from_current_shard(entity)
```

## Questions to Ask

Before implementing database changes:

1. **Data Model**: Is this data better suited for documents (MongoDB) or tables (PostgreSQL)?
2. **Query Patterns**: What are the most common access patterns for this data?
3. **Consistency Requirements**: Does this operation require strong consistency?
4. **Performance Requirements**: What are the latency and throughput requirements?
5. **Scalability**: How will this scale as data volume grows?
6. **Backup Strategy**: How will this data be backed up and restored?

## Resources

### Internal Documentation
- `README.md`: Module overview and setup
- `tests/integration/test_db.py`: Database integration tests

### External References
- [MongoDB Async Driver](https://motor.readthedocs.io/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Database Design Patterns](https://microservices.io/patterns/data/database-per-service.html)

---


**For Questions**: Consult the database module tests and README for usage examples



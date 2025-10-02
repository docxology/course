# Database Module

The database module provides data persistence and storage abstraction.

## Components

- `base.py`: Abstract database interface
- `mongodb.py`: MongoDB adapter for document storage
- `postgresql.py`: PostgreSQL adapter for relational data

## Features

- Unified database interface
- Async support for scalability
- Multi-database support
- Connection pooling
- Health monitoring

## Usage

```python
from curriculum.db import DatabaseManager, MongoDBAdapter, PostgreSQLAdapter

# Register databases
db_manager = DatabaseManager()
mongo_adapter = MongoDBAdapter()
db_manager.register_database("mongodb", mongo_adapter)

# Use database
await db_manager.initialize_all()
db = db_manager.get_database("mongodb")
result = await db.get(entity_id, EntityType)
```

## Testing

```bash
pytest tests/test_db/
```


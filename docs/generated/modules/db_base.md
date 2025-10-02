# Module: db.base

**File:** `src/curriculum/db/base.py`

## Description

Database base classes and interfaces.

## Classes

### `DatabaseInterface`

Abstract base class for database operations.

**Inherits from:** ABC

**Methods:** 8


**Method List:**

- `connect`: Connect to database.

- `disconnect`: Disconnect from database.

- `create`: Create a new entity.

- `get`: Get entity by ID.

- `update`: Update existing entity.

- `delete`: Delete entity.

- `list`: List entities with optional filtering and paginati

- `count`: Count entities matching filters.

### `DatabaseManager`

Database manager for handling multiple database connections.

**Methods:** 5


**Method List:**

- `__init__`: Initialize database manager.

- `register_database`: Register a database instance.

- `get_database`: Get database instance.

- `initialize_all`: Initialize all registered databases.

- `shutdown_all`: Shutdown all registered databases.

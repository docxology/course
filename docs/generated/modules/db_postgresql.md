# Module: db.postgresql

**File:** `src/curriculum/db/postgresql.py`

## Description

PostgreSQL database adapter using SQLAlchemy.

## Classes

### `Base`

SQLAlchemy base class.

**Inherits from:** DeclarativeBase

**Methods:** 0

### `UserModel`

User table model.

**Inherits from:** Base

**Methods:** 0

### `ContentModel`

Content table model.

**Inherits from:** Base

**Methods:** 0

### `PostgreSQLAdapter`

PostgreSQL database adapter.

**Inherits from:** DatabaseInterface

**Methods:** 12


**Method List:**

- `__init__`: Initialize PostgreSQL adapter.

- `connect`: Connect to PostgreSQL database.

- `disconnect`: Disconnect from PostgreSQL database.

- `create`: Create a new entity.

- `get`: Get entity by ID.

- `update`: Update existing entity.

- `delete`: Delete entity.

- `list`: List entities with optional filtering and paginati

- `count`: Count entities matching filters.

- `_get_sql_model_class`: Map Pydantic model type to SQLAlchemy model class.

- `_pydantic_to_sqlalchemy`: Convert Pydantic model to SQLAlchemy model.

- `_sqlalchemy_to_pydantic`: Convert SQLAlchemy model to Pydantic model.

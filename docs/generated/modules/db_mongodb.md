# Module: db.mongodb

**File:** `src/curriculum/db/mongodb.py`

## Description

MongoDB database adapter.

## Classes

### `MongoDBAdapter`

MongoDB database adapter.

**Inherits from:** DatabaseInterface

**Methods:** 13


**Method List:**

- `__init__`: Initialize MongoDB adapter.

- `connect`: Connect to MongoDB database.

- `disconnect`: Disconnect from MongoDB database.

- `create`: Create a new entity.

- `get`: Get entity by ID.

- `update`: Update existing entity.

- `delete`: Delete entity.

- `list`: List entities with optional filtering and paginati

- `count`: Count entities matching filters.

- `_get_collection_name`: Get MongoDB collection name for entity type.

- `_entity_to_dict`: Convert entity to dictionary for MongoDB storage.

- `_dict_to_entity`: Convert MongoDB document to entity.

- `_is_iso_datetime`: Check if string is ISO datetime format.

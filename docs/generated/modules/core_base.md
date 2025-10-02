# Module: core.base

**File:** `src/curriculum/core/base.py`

## Description

Base models and mixins for the Curriculum Repository System.

## Classes

### `TimestampMixin`

Mixin for timestamp fields.

**Inherits from:** BaseModel

**Methods:** 1


**Method List:**

- `update_timestamp`: Update the updated_at timestamp.

### `UUIDMixin`

Mixin for UUID primary key.

**Inherits from:** BaseModel

**Methods:** 0

### `SoftDeleteMixin`

Mixin for soft delete functionality.

**Inherits from:** BaseModel

**Methods:** 2


**Method List:**

- `soft_delete`: Mark the record as deleted.

- `restore`: Restore a soft-deleted record.

### `BaseEntity`

Base entity with common fields.

**Inherits from:** UUIDMixin, TimestampMixin, SoftDeleteMixin

**Methods:** 0

### `PagedResponse`

Paged response wrapper.

**Inherits from:** BaseModel

**Methods:** 1


**Method List:**

- `create`: Create a paged response.

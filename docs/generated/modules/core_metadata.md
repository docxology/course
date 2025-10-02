# Module: core.metadata

**File:** `src/curriculum/core/metadata.py`

## Description

Metadata models following Dublin Core and LRMI standards.

## Classes

### `ResourceType`

Dublin Core resource types.

**Inherits from:** str, Enum

**Methods:** 0

### `EducationalUse`

LRMI educational use types.

**Inherits from:** str, Enum

**Methods:** 0

### `InteractivityType`

LRMI interactivity types.

**Inherits from:** str, Enum

**Methods:** 0

### `LearningResourceType`

LRMI learning resource types.

**Inherits from:** str, Enum

**Methods:** 0

### `DublinCore`

Dublin Core 15-element metadata schema.

**Inherits from:** BaseEntity

**Methods:** 0

### `LRMIMetadata`

Learning Resource Metadata Initiative (LRMI) extensions.

**Inherits from:** BaseEntity

**Methods:** 0

### `Metadata`

Comprehensive metadata combining Dublin Core and LRMI.

**Inherits from:** BaseEntity

**Methods:** 1


**Method List:**

- `create_minimal`: Create metadata with minimal required fields.

### `Taxonomy`

Custom taxonomy for content classification.

**Inherits from:** BaseEntity

**Methods:** 0

### `Tag`

Content tag.

**Inherits from:** BaseEntity

**Methods:** 2


**Method List:**

- `increment_usage`: Increment tag usage count.

- `decrement_usage`: Decrement tag usage count.

# Core Domain Documentation

**Domain:** Core Models and Base Classes
**Files:** 13 documentation files
**Focus:** Foundational components for the Curriculum Repository System

---

## Overview

The Core domain contains the foundational models, base classes, and essential components that form the backbone of the Curriculum Repository System. This includes:

- **Base Classes:** TimestampMixin, UUIDMixin, SoftDeleteMixin, BaseEntity
- **Core Models:** Assessment, User, Content, Metadata, Analytics
- **Base Infrastructure:** Database base classes and interfaces

## Files in This Domain

### Module Documentation

| Module | Description | File |
|--------|-------------|------|
| `core` | Main core module overview | [module_core.md](module_core.md) |
| `core.analytics` | Learning event tracking and analytics | [module_core_analytics.md](module_core_analytics.md) |
| `core.assessment` | Assessment and evaluation models | [module_core_assessment.md](module_core_assessment.md) |
| `core.base` | Base classes and mixins | [module_core_base.md](module_core_base.md) |
| `core.content` | Content models and lifecycle | [module_core_content.md](module_core_content.md) |
| `core.metadata` | Dublin Core and LRMI metadata | [module_core_metadata.md](module_core_metadata.md) |
| `core.user` | User and authentication models | [module_core_user.md](module_core_user.md) |

### File Documentation

| File | Module | Description | File |
|------|--------|-------------|------|
| `base.py` | core.base | Base classes and mixins | [file_base.md](file_base.md) |
| `analytics.py` | core.analytics | Learning event tracking | [file_analytics.md](file_analytics.md) |
| `assessment.py` | core.assessment | Assessment models | [file_assessment.md](file_assessment.md) |
| `content.py` | core.content | Content models | [file_content.md](file_content.md) |
| `metadata.py` | core.metadata | Metadata models | [file_metadata.md](file_metadata.md) |
| `user.py` | core.user | User models | [file_user.md](file_user.md) |

## Architecture Role

The Core domain provides:
- ✅ **Foundation:** Base classes used throughout the system
- ✅ **Data Models:** Core entities (User, Content, Assessment, etc.)
- ✅ **Standards Compliance:** Dublin Core, LRMI, xAPI
- ✅ **Common Patterns:** Timestamp, UUID, soft delete functionality

## Related Domains

- **Content:** Uses core content models
- **Learning:** Uses core assessment and analytics models
- **Database:** Uses core base classes
- **Tools:** Uses core base classes

## Navigation

### Parent Domains
- [📁 Root](../index.md)
- [📁 All Domains](../index.md)

### Related Domains
- [📁 Content](../content/index.md) - Content management
- [📁 Learning](../learning/index.md) - Learning features
- [📁 Database](../db/index.md) - Data layer
- [📁 Tools](../tools/index.md) - Utilities

---

**Generated:** October 1, 2025
**Documentation:** Core Domain Index


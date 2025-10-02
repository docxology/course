# Module: config

**File:** `src/curriculum/config.py`

## Description

Configuration management for the Curriculum Repository System.

## Classes

### `Settings`

Application settings loaded from environment variables.

**Inherits from:** BaseSettings

**Methods:** 3


**Method List:**

- `allowed_extensions_list`: Get allowed file extensions as a list.

- `is_production`: Check if running in production environment.

- `is_development`: Check if running in development environment.

## Functions

### `get_settings`

Get cached settings instance.

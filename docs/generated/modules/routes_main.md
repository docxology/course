# Module: routes.main

**File:** `src/curriculum/routes/main.py`

## Description

Main FastAPI application for Curriculum Repository System.

## Functions

### `lifespan`

Application lifespan manager.

**Parameters:**

- `app: FastAPI`

### `add_process_time_header`

Add processing time to response headers.

**Parameters:**

- `request: Request`

- `call_next`

### `health_check`

Health check endpoint.

### `global_exception_handler`

Global exception handler.

**Parameters:**

- `request: Request`

- `exc: Exception`

# AI Agents Guide - Routes Module

## Overview

The routes module provides REST API endpoints for the Curriculum Repository System, implementing a clean separation between API concerns and business logic. All endpoints follow RESTful conventions and include comprehensive authentication, validation, and error handling.

## Module Structure

```
routes/
├── main.py            # FastAPI application setup and configuration
├── content.py         # Content management endpoints
├── users.py           # User management and authentication
├── assessments.py     # Assessment and grading endpoints
├── analytics.py       # Analytics and reporting endpoints
├── dependencies.py    # Shared authentication and validation
├── __init__.py        # Module exports
├── README.md          # Module documentation
└── AGENTS.md          # This file
```

## API Architecture

### FastAPI Application Setup

1. **Application Factory Pattern**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")

    # Initialize services
    await initialize_services()

    yield

    # Shutdown
    await cleanup_services()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive educational content management platform",
    lifespan=lifespan
)
```

2. **CORS Configuration**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

3. **Exception Handlers**:
```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

## Endpoint Design Patterns

### Content Endpoints

1. **CRUD Operations**:
```python
@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: CreateContentRequest,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service)
) -> ContentResponse:
    """Create new content."""
    if not current_user.has_permission(ContentPermission.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    content = content_service.create_content(
        title=content_data.title,
        content_type=content_data.content_type,
        format=content_data.format,
        author_id=current_user.id,
        description=content_data.description,
        content_body=content_data.content_body
    )

    return ContentResponse.model_validate(content)
```

2. **Resource Relationships**:
```python
@router.get("/{content_id}/children", response_model=List[ContentResponse])
async def get_content_children(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service)
) -> List[ContentResponse]:
    """Get child content items."""
    parent_content = content_service.get_content(content_id)
    if not parent_content:
        raise HTTPException(status_code=404, detail="Parent content not found")

    if not current_user.can_access_content(parent_content):
        raise HTTPException(status_code=403, detail="Access denied")

    children = content_service.get_children(content_id)
    return [ContentResponse.model_validate(child) for child in children]
```

3. **Search and Filtering**:
```python
@router.get("/search", response_model=SearchResultsResponse)
async def search_content(
    q: str = Query(..., min_length=1, description="Search query"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    tags: List[str] = Query([], description="Filter by tags"),
    author_id: Optional[UUID] = Query(None, description="Filter by author"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service)
) -> SearchResultsResponse:
    """Search content with advanced filters."""
    # Validate search permissions
    if not current_user.has_permission(ContentPermission.SEARCH):
        raise HTTPException(status_code=403, detail="Search permission required")

    results = content_service.search_content(
        query=q,
        content_type=content_type,
        tags=tags,
        author_id=author_id,
        page=page,
        page_size=page_size
    )

    return SearchResultsResponse(
        items=[ContentResponse.model_validate(item) for item in results.items],
        total=results.total,
        page=results.page,
        page_size=results.page_size,
        total_pages=(results.total + page_size - 1) // page_size
    )
```

### User Management Endpoints

1. **Authentication Flow**:
```python
@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> LoginResponse:
    """Authenticate user and return tokens."""
    user = auth_service.authenticate_user(
        credentials.username_or_email,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated"
        )

    # Generate tokens
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    # Record login
    auth_service.record_login(user.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user)
    )
```

2. **Role-Based Access Control**:
```python
@router.post("/{user_id}/roles")
async def add_user_role(
    user_id: UUID,
    role_data: AddRoleRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, str]:
    """Add role to user (admin only)."""
    if not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(status_code=403, detail="Admin permission required")

    target_user = user_service.get_user(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = user_service.add_role(user_id, role_data.role)

    return {"message": f"Role {role_data.role} added to user {target_user.username}"}
```

3. **Password Management**:
```python
@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> Dict[str, str]:
    """Change user password."""
    success = user_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    return {"message": "Password changed successfully"}
```

### Assessment Endpoints

1. **Assessment Creation**:
```python
@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment_data: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> AssessmentResponse:
    """Create new assessment."""
    if not current_user.has_permission(AssessmentPermission.CREATE):
        raise HTTPException(status_code=403, detail="Assessment creation permission required")

    assessment = assessment_service.create_assessment(
        title=assessment_data.title,
        description=assessment_data.description,
        time_limit=assessment_data.time_limit,
        passing_score=assessment_data.passing_score,
        max_attempts=assessment_data.max_attempts,
        created_by=current_user.id
    )

    return AssessmentResponse.model_validate(assessment)
```

2. **Submission Handling**:
```python
@router.post("/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: UUID,
    submission_data: SubmitAssessmentRequest,
    current_user: User = Depends(get_current_user),
    assessment_service: AssessmentService = Depends(get_assessment_service)
) -> SubmissionResponse:
    """Submit assessment for grading."""
    # Validate submission
    submission = assessment_service.submit_assessment(
        assessment_id=assessment_id,
        user_id=current_user.id,
        answers=submission_data.answers,
        time_taken=submission_data.time_taken
    )

    if not submission:
        raise HTTPException(status_code=400, detail="Submission failed")

    # Auto-grade if configured
    if submission.assessment.auto_grade:
        graded_submission = assessment_service.grade_submission(submission.id)
        return SubmissionResponse.model_validate(graded_submission)

    return SubmissionResponse.model_validate(submission)
```

### Analytics Endpoints

1. **Event Tracking**:
```python
@router.post("/track", status_code=status.HTTP_204_NO_CONTENT)
async def track_event(
    event_data: TrackEventRequest,
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> None:
    """Track learning event."""
    analytics_service.track_event(
        user_id=current_user.id,
        verb=event_data.verb,
        event_type=event_data.event_type,
        object_id=event_data.object_id,
        object_type=event_data.object_type,
        success=event_data.success,
        score=event_data.score,
        duration=event_data.duration,
        metadata=event_data.metadata
    )
```

2. **Report Generation**:
```python
@router.get("/reports/user/{user_id}", response_model=UserAnalyticsReport)
async def get_user_analytics_report(
    user_id: UUID,
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
) -> UserAnalyticsReport:
    """Get comprehensive user analytics report."""
    if user_id != current_user.id and not current_user.has_permission(AnalyticsPermission.VIEW_ALL):
        raise HTTPException(status_code=403, detail="Cannot view other users' reports")

    report = analytics_service.generate_user_report(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

    return UserAnalyticsReport.model_validate(report)
```

## Authentication & Authorization

### JWT Token Management

1. **Token Generation**:
```python
def create_access_token(self, user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes)),
        "iat": datetime.utcnow()
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def create_refresh_token(self, user_id: UUID) -> str:
    """Create JWT refresh token."""
    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        "iat": datetime.utcnow()
    }

    return jwt.encode(to_encode, settings.refresh_key, algorithm=settings.algorithm)
```

2. **Token Verification**:
```python
async def verify_token(self, token: str, expected_type: str = "access") -> Optional[UUID]:
    """Verify JWT token and extract user ID."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_type = payload.get("type")
        user_id = payload.get("sub")

        if token_type != expected_type or not user_id:
            return None

        return UUID(user_id)
    except JWTError:
        return None
```

3. **Refresh Token Flow**:
```python
@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh access token using refresh token."""
    user_id = auth_service.verify_token(refresh_data.refresh_token, "refresh")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = auth_service.user_service.get_user(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Generate new access token
    access_token = auth_service.create_access_token(user_id)

    return TokenResponse(access_token=access_token, token_type="bearer")
```

## Request/Response Models

### Pydantic Models

1. **Request Models**:
```python
class CreateContentRequest(BaseModel):
    """Request model for creating content."""
    title: str = Field(min_length=1, max_length=500)
    content_type: ContentType
    format: ContentFormat
    description: Optional[str] = Field(None, max_length=2000)
    content_body: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    parent_id: Optional[UUID] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Introduction to Python",
                "content_type": "lesson",
                "format": "markdown",
                "description": "Learn Python basics",
                "content_body": "# Python Basics\\n\\nPython is a programming language.",
                "tags": ["python", "programming", "beginner"]
            }
        }
```

2. **Response Models**:
```python
class ContentResponse(BaseModel):
    """Response model for content data."""
    id: str
    title: str
    content_type: str
    format: str
    status: str
    author_id: str
    description: Optional[str]
    tags: List[str]
    view_count: int
    download_count: int
    created_at: str
    updated_at: str
    parent_id: Optional[str]
    children_count: int

    @classmethod
    def from_content(cls, content: Content) -> 'ContentResponse':
        return cls(
            id=str(content.id),
            title=content.title,
            content_type=content.content_type.value,
            format=content.format.value,
            status=content.status.value,
            author_id=str(content.author_id),
            description=content.description,
            tags=content.tags,
            view_count=content.view_count,
            download_count=content.download_count,
            created_at=content.created_at.isoformat(),
            updated_at=content.updated_at.isoformat(),
            parent_id=str(content.parent_id) if content.parent_id else None,
            children_count=len(content.children) if hasattr(content, 'children') else 0
        )
```

## Error Handling

### Custom Exception Handlers

1. **Business Logic Errors**:
```python
class ContentNotFoundError(HTTPException):
    def __init__(self, content_id: UUID):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content with ID {content_id} not found"
        )

class InsufficientPermissionsError(HTTPException):
    def __init__(self, required_permission: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{required_permission}' required"
        )
```

2. **Validation Errors**:
```python
class ValidationErrorResponse(BaseModel):
    """Standard validation error response."""
    detail: List[Dict[str, Any]]
    body: Optional[Dict[str, Any]]

    @classmethod
    def from_pydantic_error(cls, error: ValidationError, body: Dict) -> 'ValidationErrorResponse':
        return cls(detail=error.errors(), body=body)
```

3. **Global Error Handler**:
```python
@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationErrorResponse.from_pydantic_error(exc, await request.json()).model_dump()
    )
```

## Testing Guidelines

### API Testing Patterns

1. **Authentication Testing**:
```python
class TestContentAPI:
    def test_create_content_unauthorized(self, client: TestClient):
        response = client.post("/api/v1/content/")
        assert response.status_code == 401

    def test_create_content_authorized(self, client: TestClient, auth_headers: Dict):
        content_data = {
            "title": "Test Content",
            "content_type": "lesson",
            "format": "markdown"
        }
        response = client.post("/api/v1/content/", json=content_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Content"
```

2. **Integration Testing**:
```python
@pytest.mark.integration
async def test_full_content_workflow(self, client: TestClient, auth_headers: Dict):
    # Create content
    content_data = {
        "title": "Test Lesson",
        "content_type": "lesson",
        "format": "markdown",
        "content_body": "# Test Content"
    }
    response = client.post("/api/v1/content/", json=content_data, headers=auth_headers)
    assert response.status_code == 201
    content_id = response.json()["id"]

    # Update content
    update_data = {"title": "Updated Lesson"}
    response = client.put(f"/api/v1/content/{content_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200

    # Get content
    response = client.get(f"/api/v1/content/{content_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Lesson"
```

3. **Performance Testing**:
```python
@pytest.mark.performance
async def test_api_performance(self, client: TestClient, auth_headers: Dict):
    # Test response times
    start_time = time.time()
    response = client.get("/api/v1/content/", headers=auth_headers)
    end_time = time.time()

    assert response.status_code == 200
    assert end_time - start_time < 0.5  # Should respond in under 500ms
```

## Security Considerations

### Input Validation

1. **SQL Injection Prevention**:
```python
# All database queries use parameterized queries through ORM
# No raw SQL strings in API endpoints

@router.get("/content/search")
async def search_content(
    q: str = Query(..., min_length=1, max_length=200, regex=r"^[a-zA-Z0-9\s\-_]+$"),
    # Query parameters are validated by Pydantic
):
    results = content_service.search_content(q)
    return results
```

2. **XSS Prevention**:
```python
# Content is sanitized during rendering
# User input is validated and escaped

@router.post("/content")
async def create_content(content_data: CreateContentRequest):
    # content_data is validated by Pydantic
    # HTML content is sanitized during rendering
    content = content_service.create_content(**content_data.model_dump())
    return content
```

3. **CSRF Protection**:
```python
# JWT tokens include origin validation
# CORS is properly configured

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)
```

### Rate Limiting

1. **Rate Limiting Middleware**:
```python
# TODO: Implement rate limiting
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# limiter = Limiter(key_func=get_remote_address)
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# @app.middleware("http")
# async def add_rate_limit_headers(request: Request, call_next):
#     response = await call_next(request)
#     # Add rate limit headers
#     return response
```

2. **Brute Force Protection**:
```python
# Authentication endpoints have built-in rate limiting
# Failed login attempts are tracked and limited

@router.post("/login")
async def login(credentials: LoginRequest):
    # Check for too many failed attempts
    if await auth_service.is_rate_limited(credentials.username_or_email):
        raise HTTPException(status_code=429, detail="Too many login attempts")

    # Authenticate user
    user = auth_service.authenticate_user(...)
    if not user:
        # Record failed attempt for rate limiting
        await auth_service.record_failed_login(credentials.username_or_email)
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

## Performance Optimization

### Caching Strategies

1. **Response Caching**:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup():
    redis = redis.Redis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@router.get("/content/{content_id}")
@cache(expire=300)  # Cache for 5 minutes
async def get_content(content_id: UUID):
    content = content_service.get_content(content_id)
    return ContentResponse.model_validate(content)
```

2. **Database Query Optimization**:
```python
# Use async database sessions
# Implement connection pooling
# Add database indexes for common queries

@router.get("/content/search")
async def search_content(q: str):
    # Query is optimized with database indexes
    results = await content_service.search_content_async(q)
    return results
```

### Async/Await Patterns

1. **Non-Blocking Operations**:
```python
@router.post("/content/bulk-import")
async def bulk_import_content(
    files: List[UploadFile],
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """Import multiple content files asynchronously."""
    # Start background processing
    background_tasks.add_task(
        process_content_files,
        files,
        current_user.id
    )

    return {"message": "Import started", "status": "processing"}
```

2. **Background Tasks**:
```python
async def process_content_files(files: List[UploadFile], user_id: UUID) -> None:
    """Process uploaded files in background."""
    for file in files:
        try:
            content = await parse_and_create_content(file, user_id)
            logger.info(f"Imported content: {content.title}")
        except Exception as e:
            logger.error(f"Failed to import {file.filename}: {e}")
```

## API Documentation

### OpenAPI/Swagger Integration

1. **Automatic Documentation**:
```python
# FastAPI automatically generates OpenAPI schema
# Available at /docs (Swagger UI) and /redoc (ReDoc)

app = FastAPI(
    title="Curriculum Repository API",
    description="""
    A comprehensive educational content management platform.

    ## Authentication
    All endpoints (except login) require JWT authentication.

    Include the token in the Authorization header:
    `Authorization: Bearer <your-jwt-token>`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

2. **Custom Documentation**:
```python
@router.post("/content/", response_model=ContentResponse)
async def create_content(
    content_data: CreateContentRequest,
    current_user: User = Depends(get_current_user)
) -> ContentResponse:
    """
    Create new educational content.

    This endpoint allows authorized users to create new content items.
    The content will be created in DRAFT status and can be published
    after review and approval.

    **Permissions Required:**
    - `content:create` permission

    **Rate Limits:**
    - 100 requests per minute per user

    **Example Request:**
    ```json
    {
      "title": "Introduction to Python",
      "content_type": "lesson",
      "format": "markdown",
      "description": "Learn Python basics",
      "content_body": "# Python Basics\\n\\nPython is a programming language."
    }
    ```
    """
    # Implementation...
```

## Monitoring and Observability

### Logging Strategy

1. **Request Logging**:
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(
        "API Request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "user_agent": request.headers.get("user-agent"),
            "ip": request.client.host if request.client else None
        }
    )

    return response
```

2. **Error Tracking**:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log error details
    logger.error(
        "Unhandled exception",
        extra={
            "error": str(exc),
            "type": type(exc).__name__,
            "url": str(request.url),
            "method": request.method,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

### Metrics Collection

1. **Performance Metrics**:
```python
@app.on_event("startup")
async def start_metrics_collection():
    # Start collecting metrics
    asyncio.create_task(collect_api_metrics())

async def collect_api_metrics() -> None:
    while True:
        # Collect metrics
        metrics = {
            "active_connections": len(app.state.connections) if hasattr(app.state, 'connections') else 0,
            "request_rate": get_request_rate(),
            "error_rate": get_error_rate(),
            "average_response_time": get_average_response_time()
        }

        # Send to monitoring system
        await send_metrics_to_monitoring(metrics)

        await asyncio.sleep(60)  # Collect every minute
```

## Versioning Strategy

### API Versioning

1. **URL Versioning**:
```python
# Version in URL path
@router.get("/v1/content/{content_id}")
async def get_content_v1(content_id: UUID):
    # V1 implementation
    pass

@router.get("/v2/content/{content_id}")
async def get_content_v2(content_id: UUID):
    # V2 implementation with enhanced features
    pass
```

2. **Header Versioning**:
```python
# Version in Accept header
@router.get("/content/{content_id}")
async def get_content(
    content_id: UUID,
    accept_version: str = Header("v1", alias="Accept-Version")
):
    if accept_version == "v2":
        return await get_content_v2(content_id)
    else:
        return await get_content_v1(content_id)
```

## Deployment Considerations

### Production Configuration

1. **Security Headers**:
```python
# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

2. **HTTPS Enforcement**:
```python
# Redirect HTTP to HTTPS in production
@app.middleware("http")
async def enforce_https(request: Request, call_next):
    if settings.environment == "production" and not request.url.scheme == "https":
        return RedirectResponse(url=request.url.replace(scheme="https"))
    return await call_next(request)
```

### Scalability

1. **Load Balancing**:
```python
# Support for multiple workers
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Multiple workers for load balancing
        reload=settings.environment == "development"
    )
```

2. **Database Connection Pooling**:
```python
# Configure connection pooling for production
@app.on_event("startup")
async def configure_db_pools():
    # MongoDB connection pool
    settings.mongodb_max_pool_size = 20
    settings.mongodb_min_pool_size = 5

    # PostgreSQL connection pool
    settings.postgresql_pool_size = 20
    settings.postgresql_max_overflow = 0
```

## Common Issues and Solutions

### Authentication Issues

1. **Token Expiration**:
```python
# Handle token expiration gracefully
@router.get("/protected-endpoint")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    try:
        # Use current_user
        return {"user": current_user.username}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
```

2. **Permission Denied**:
```python
# Clear permission error messages
@router.delete("/content/{content_id}")
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user)
):
    if not current_user.has_permission(ContentPermission.DELETE):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this content"
        )
```

### Performance Issues

1. **Slow Database Queries**:
```python
# Add database query logging
@app.middleware("http")
async def log_db_queries(request: Request, call_next):
    # Track database query count and time
    db_metrics = {"query_count": 0, "query_time": 0.0}

    # Monkey patch database methods to track metrics
    original_execute = database_session.execute
    def tracked_execute(*args, **kwargs):
        db_metrics["query_count"] += 1
        start_time = time.time()
        result = original_execute(*args, **kwargs)
        db_metrics["query_time"] += time.time() - start_time
        return result

    database_session.execute = tracked_execute

    response = await call_next(request)

    # Log if queries are slow
    if db_metrics["query_time"] > 1.0:
        logger.warning(f"Slow endpoint: {request.url.path}, queries: {db_metrics}")

    return response
```

## Best Practices

### API Design

1. **RESTful Conventions**:
   - Use appropriate HTTP methods (GET, POST, PUT, DELETE)
   - Use resource-based URLs (`/api/v1/content/{id}`)
   - Return appropriate status codes (200, 201, 400, 404, 500)
   - Include meaningful error messages

2. **Response Consistency**:
   - Standardize response formats
   - Include pagination metadata
   - Provide filtering and sorting options
   - Document all endpoints with examples

3. **Security First**:
   - Validate all inputs
   - Implement proper authentication
   - Use HTTPS in production
   - Rate limit sensitive endpoints

### Code Organization

1. **Separation of Concerns**:
   - Route handlers focus on HTTP concerns
   - Business logic stays in services
   - Models handle data validation
   - Dependencies handle cross-cutting concerns

2. **Dependency Injection**:
   - Use FastAPI's dependency injection system
   - Keep route handlers clean and focused
   - Make services easily testable
   - Enable easy mocking for tests

## Extension Points

### Custom Middleware

1. **API Key Authentication**:
```python
@app.middleware("http")
async def api_key_auth(request: Request, call_next):
    # Check for API key in header
    api_key = request.headers.get("X-API-Key")
    if not api_key or not await validate_api_key(api_key):
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

    response = await call_next(request)
    return response
```

2. **Request/Response Transformation**:
```python
@app.middleware("http")
async def transform_requests(request: Request, call_next):
    # Modify request before processing
    if request.path.startswith("/api/v1/"):
        # Add API versioning header
        request.state.api_version = "v1"

    response = await call_next(request)

    # Modify response after processing
    if hasattr(response, 'headers'):
        response.headers["X-API-Version"] = "v1"

    return response
```

### Custom Serializers

1. **JSON Serialization**:
```python
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

@router.get("/content/{content_id}")
async def get_content(content_id: UUID):
    content = content_service.get_content(content_id)

    # Custom serialization for complex objects
    content_data = jsonable_encoder(content, custom_encoder={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

    return JSONResponse(content=content_data)
```

2. **Alternative Response Formats**:
```python
@router.get("/content/{content_id}/pdf")
async def get_content_pdf(content_id: UUID):
    content = content_service.get_content(content_id)

    # Generate PDF response
    pdf_data = await generate_pdf(content)

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={content.title}.pdf"}
    )
```

## Questions to Ask

Before adding new API endpoints:

1. **Security**: Does this endpoint need authentication? What permissions are required?
2. **Validation**: What input validation is needed? Are there business rules to enforce?
3. **Performance**: Will this endpoint handle large datasets? Does it need caching?
4. **Documentation**: Is the endpoint well-documented with examples?
5. **Testing**: Are there comprehensive tests for success and failure cases?
6. **Versioning**: Does this change break existing clients? Is versioning needed?

## Resources

### Internal Documentation
- `README.md`: Module overview and API structure
- `tests/integration/test_routes.py`: API integration tests

### External References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [REST API Design](https://restfulapi.net/)
- [JWT Authentication](https://jwt.io/)
- [OpenAPI Specification](https://www.openapis.org/)

---


**For Questions**: Review the API documentation at `/docs` when running the server



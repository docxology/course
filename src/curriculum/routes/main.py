"""Main FastAPI application for Curriculum Repository System."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from curriculum.config import settings
from curriculum.routes import content, users, assessments, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")

    yield

    # Shutdown
    print(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive educational content management platform",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": time.time(),
    }


# API routes
app.include_router(
    content.router,
    prefix="/api/v1/content",
    tags=["content"],
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"],
)

app.include_router(
    assessments.router,
    prefix="/api/v1/assessments",
    tags=["assessments"],
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "path": str(request.url.path),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "curriculum.routes.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

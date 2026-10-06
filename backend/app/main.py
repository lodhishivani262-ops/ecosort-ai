"""EcoSort AI - Main FastAPI Application Entry Point.

AI-Based Household Waste Segregation Assistant (SDG 12: Responsible Consumption)
Tagline: "Identify it. Sort it. Dispose responsibly."
"""

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.rate_limit import limiter, rate_limit_handler
from app.core.security import (
    AppException,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)

# Initialize application logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and graceful shutdown lifecycles."""
    logger.info(
        f"Starting {settings.APP_NAME} [Environment: {settings.APP_ENV}]"
    )
    # Ensure database schema is present & enforce data retention policy
    try:
        from app.db.base import Base
        from app.db.database import engine, SessionLocal
        Base.metadata.create_all(bind=engine)

        if settings.DATA_RETENTION_DAYS > 0:
            db = SessionLocal()
            try:
                from app.repositories.classification_repository import ClassificationRepository
                repo = ClassificationRepository(db)
                pruned = repo.delete_older_than(settings.DATA_RETENTION_DAYS)
                if pruned > 0:
                    logger.info(
                        f"Data retention policy applied: pruned {pruned} records older than {settings.DATA_RETENTION_DAYS} days."
                    )
            except Exception as ret_err:
                logger.warning(f"Data retention cleanup check warning: {ret_err}")
            finally:
                db.close()
    except Exception as db_err:
        logger.warning(f"Database startup initialization warning: {db_err}")

    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "Public API for EcoSort AI: An AI-Assisted Household Waste Segregation & Disposal Guidance Platform. "
        "Aligned with UN Sustainable Development Goal 12 (Responsible Consumption & Production)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Attach rate limiter instance to application state
app.state.limiter = limiter

# ------------------------------------------------------------------------------
# Exception Handlers (Consistent JSON Error Responses)
# ------------------------------------------------------------------------------


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles structured domain and validation exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Transforms raw FastAPI/Pydantic validation errors into clean API error format."""
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field_loc = " -> ".join([str(loc) for loc in first_error.get("loc", []) if loc != "body"])
        raw_msg = first_error.get("msg", "Invalid request parameter.")
        if raw_msg.startswith("Value error, "):
            raw_msg = raw_msg[len("Value error, "):]
        message = f"{field_loc}: {raw_msg}" if field_loc else raw_msg
    else:
        message = "Invalid request payload."

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"code": "VALIDATION_ERROR", "message": message}},
    )


@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Handles API rate limit exceedances."""
    return rate_limit_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Standardizes standard HTTP exceptions (404, 405, etc.)."""
    error_code = f"HTTP_{exc.status_code}"
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        error_code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        error_code = "METHOD_NOT_ALLOWED"
    elif exc.status_code == status.HTTP_409_CONFLICT:
        error_code = "RESOURCE_CONFLICT"
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        error_code = "FORBIDDEN"

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": error_code, "message": str(exc.detail)}},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catches unexpected exceptions; prevents leaking internal stack traces or paths."""
    req_id = getattr(request.state, "request_id", "unknown")
    logger.critical(
        f"[REQ-{req_id}] Unhandled server exception: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Please try again later.",
            }
        },
    )


# ------------------------------------------------------------------------------
# Middlewares
# ------------------------------------------------------------------------------

# 1. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. CORS Middleware (Origins strictly governed by ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
)

# 3. Request Context & Access Logging Middleware
app.add_middleware(RequestContextMiddleware)


# ------------------------------------------------------------------------------
# Core Root & Direct Health Probes
# ------------------------------------------------------------------------------


@app.get(
    "/",
    summary="Root Service Metadata",
    description="Provides basic service identity, verification message, and current API version.",
    tags=["System"],
)
async def get_root() -> dict:
    """Root metadata verification endpoint."""
    return {
        "name": settings.APP_NAME,
        "message": f"{settings.APP_NAME} backend is running",
        "version": settings.VERSION,
    }


@app.get(
    "/health",
    summary="Root Health Check",
    description="Lightweight health check endpoint for cloud platform deployment probes.",
    tags=["System"],
)
async def get_root_health() -> dict:
    """Lightweight deployment health probe."""
    return {"status": "healthy", "service": "ecosort-ai-backend"}


# ------------------------------------------------------------------------------
# Mount API Version Routers
# ------------------------------------------------------------------------------

app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import os
    import uvicorn

    server_port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=server_port, reload=False)

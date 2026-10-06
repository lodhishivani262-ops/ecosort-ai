"""EcoSort AI - Rate Limiter Setup and Error Formatting."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.config import settings

# Global in-memory rate limiter using client IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT],
    headers_enabled=False,
)


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Standardized error handler for rate limit exceedances."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Too many requests. Rate limit of {exc.detail} exceeded. Please wait before retrying.",
            }
        },
    )

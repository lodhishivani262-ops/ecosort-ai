"""EcoSort AI - Security Middleware, Headers, and Application Exceptions."""

import time
import uuid
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.config import settings

logger = logging.getLogger("ecosort")


class AppException(Exception):
    """Base application exception for handled errors."""

    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationException(AppException):
    """Raised when input validation fails."""

    def __init__(self, code: str = "VALIDATION_ERROR", message: str = "Invalid input data.", status_code: int = 400):
        super().__init__(code=code, message=message, status_code=status_code)


class FileValidationException(AppException):
    """Raised when an uploaded file violates security or format rules."""

    def __init__(self, code: str = "INVALID_FILE_TYPE", message: str = "Invalid file.", status_code: int = 400):
        super().__init__(code=code, message=message, status_code=status_code)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to protect against common web vulnerabilities."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Prevent browser from MIME-sniffing away from declared Content-Type
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Protect against clickjacking by denying framing
        response.headers["X-Frame-Options"] = "DENY"

        # Control referrer information sent in HTTP requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Enable XSS filtering in supporting browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS via HSTS if in production environment
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Generates unique Request ID, measures processing latency, and logs structured request info."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # Capture or generate unique request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Attach request_id to logger context
        extra = {"request_id": request_id}

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} failed with unhandled exception: {exc} ({duration_ms:.2f}ms)",
                extra=extra,
                exc_info=settings.DEBUG,
            )
            raise exc

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Inject tracing headers into response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        # Clean access logging (excluding bodies/binary contents)
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms)",
            extra=extra,
        )

        return response

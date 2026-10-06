"""EcoSort AI - Common Schemas and Standard Response Models."""

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error payload details."""

    code: str = Field(..., description="Machine-readable error code", examples=["INVALID_FILE_TYPE"])
    message: str = Field(..., description="Human-readable explanation of the error", examples=["Unsupported image format."])


class ErrorResponse(BaseModel):
    """Standardized top-level error response envelope."""

    error: ErrorDetail


class StandardResponse(BaseModel, Generic[T]):
    """Standard success wrapper envelope."""

    success: bool = Field(default=True, description="Whether the operation succeeded")
    data: T = Field(..., description="The primary response payload")
    message: Optional[str] = Field(default=None, description="Optional informational message")

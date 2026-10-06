"""EcoSort AI - Feedback Schemas (Stage 5)."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FeedbackType(str, Enum):
    """Controlled feedback categories for classification accuracy and usability."""

    HELPFUL = "HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"
    INCORRECT_CATEGORY = "INCORRECT_CATEGORY"
    INCORRECT_IDENTIFICATION = "INCORRECT_IDENTIFICATION"
    UNCLEAR_GUIDANCE = "UNCLEAR_GUIDANCE"
    OTHER = "OTHER"


class FeedbackCreate(BaseModel):
    """Schema for validating submitted user feedback."""

    request_id: str = Field(
        ...,
        min_length=10,
        max_length=64,
        description="Correlation ID (UUID) of the classification event",
        examples=["8f87e5b3-34e8-46c5-a22b-47e1d51a61c3"],
    )
    rating: Optional[int] = Field(
        default=None,
        ge=1,
        le=5,
        description="Optional rating strictly bounded between 1 (poor) and 5 (excellent)",
        examples=[5],
    )
    feedback_type: FeedbackType = Field(
        ...,
        description="Controlled category of feedback",
        examples=[FeedbackType.HELPFUL],
    )
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional short user comment, maximum 500 characters",
        examples=["Very clear instructions on rinsing the container."],
    )

    @field_validator("comment")
    @classmethod
    def sanitize_comment(cls, v: Optional[str]) -> Optional[str]:
        """Strips excessive whitespace and rejects empty string comments."""
        if v is None:
            return None
        cleaned = v.strip()
        if not cleaned:
            return None
        return cleaned

    @field_validator("request_id")
    @classmethod
    def sanitize_request_id(cls, v: str) -> str:
        """Sanitizes request_id."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("request_id cannot be empty or blank.")
        return cleaned


class FeedbackResponse(BaseModel):
    """User-facing acknowledgment response for submitted feedback."""

    success: bool = Field(default=True, description="Whether feedback was accepted")
    message: str = Field(
        default="Thank you for your feedback.",
        description="Human-friendly feedback confirmation message",
    )
    request_id: str = Field(..., description="Associated request identifier")
    created_at: datetime = Field(..., description="Timestamp of feedback submission")

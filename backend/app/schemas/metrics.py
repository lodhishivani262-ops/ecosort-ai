"""EcoSort AI - Aggregated Metrics Schemas (Stage 5).

STRICT PRIVACY: Exposes strictly aggregated data without individual user records,
IP addresses, image references, or personal information.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    """Distribution metrics for an individual waste category."""

    category: str = Field(..., description="Waste category name")
    count: int = Field(..., description="Number of classifications assigned to this category")
    percentage: float = Field(..., description="Percentage of total classifications")


class FeedbackMetrics(BaseModel):
    """Aggregated feedback and satisfaction statistics."""

    total_feedback: int = Field(default=0, description="Total feedback submissions received")
    helpful_count: int = Field(default=0, description="Count of positive/helpful feedback")
    not_helpful_count: int = Field(default=0, description="Count of unhelpful feedback")
    helpful_percentage: float = Field(default=0.0, description="Percentage of feedback marked helpful")
    average_rating: Optional[float] = Field(
        default=None,
        description="Average numerical rating (1-5 scale) across submissions with ratings",
    )
    type_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by feedback_type",
    )


class MetricsResponse(BaseModel):
    """Comprehensive high-level application metrics."""

    total_classifications: int = Field(..., description="Total classification requests processed")
    successful_classifications: int = Field(..., description="Count of successfully classified items")
    failed_classifications: int = Field(..., description="Count of failed classification attempts")
    average_processing_time_ms: float = Field(..., description="Average processing duration in milliseconds")
    low_confidence_percentage: float = Field(
        ...,
        description="Percentage of classifications flagged with LOW confidence",
    )
    categories: List[CategoryBreakdown] = Field(
        default_factory=list,
        description="Distribution of classifications across waste categories",
    )
    feedback: FeedbackMetrics = Field(
        default_factory=FeedbackMetrics,
        description="Aggregated user feedback and satisfaction metrics",
    )

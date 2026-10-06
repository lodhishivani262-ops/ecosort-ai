"""EcoSort AI - Aggregated Metrics Service (Stage 5).

Aggregates operational metrics, classification distribution, and user satisfaction scores.
PRIVACY GUARANTEE: Never exposes individual records, user metadata, or identifiers.
"""

import logging
from sqlalchemy.orm import Session
from app.repositories.classification_repository import ClassificationRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.metrics import CategoryBreakdown, FeedbackMetrics, MetricsResponse

logger = logging.getLogger("ecosort.metrics")


class MetricsService:
    """Service computing aggregated usage and quality metrics."""

    def __init__(self, db: Session):
        self.db = db
        self.classification_repo = ClassificationRepository(db)
        self.feedback_repo = FeedbackRepository(db)

    def get_metrics(self) -> MetricsResponse:
        """Returns comprehensive aggregated system metrics."""
        cls_metrics = self.classification_repo.get_aggregated_metrics()
        fb_metrics = self.feedback_repo.get_feedback_metrics()

        categories = [
            CategoryBreakdown(
                category=c["category"],
                count=c["count"],
                percentage=c["percentage"],
            )
            for c in cls_metrics["categories"]
        ]

        feedback = FeedbackMetrics(
            total_feedback=fb_metrics["total_feedback"],
            helpful_count=fb_metrics["helpful_count"],
            not_helpful_count=fb_metrics["not_helpful_count"],
            helpful_percentage=fb_metrics["helpful_percentage"],
            average_rating=fb_metrics["average_rating"],
            type_breakdown=fb_metrics["type_breakdown"],
        )

        return MetricsResponse(
            total_classifications=cls_metrics["total_classifications"],
            successful_classifications=cls_metrics["successful_classifications"],
            failed_classifications=cls_metrics["failed_classifications"],
            average_processing_time_ms=cls_metrics["average_processing_time_ms"],
            low_confidence_percentage=cls_metrics["low_confidence_percentage"],
            categories=categories,
            feedback=feedback,
        )

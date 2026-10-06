"""EcoSort AI - Feedback Repository (Stage 5).

Data access layer for user feedback reviews and satisfaction metrics.
"""

from typing import Any, Dict, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.models import Feedback


class FeedbackRepository:
    """Encapsulates all database operations for the Feedback model."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, feedback: Feedback) -> Feedback:
        """Persists a new user feedback record with transaction safety."""
        try:
            self.db.add(feedback)
            self.db.commit()
            self.db.refresh(feedback)
            return feedback
        except Exception:
            self.db.rollback()
            raise

    def get_by_request_id(self, request_id: str) -> Optional[Feedback]:
        """Finds feedback submitted for a specific request ID."""
        stmt = select(Feedback).where(Feedback.request_id == request_id)
        return self.db.scalars(stmt).first()

    def get_feedback_metrics(self) -> Dict[str, Any]:
        """Calculates aggregated feedback statistics without exposing individual records."""
        total = self.db.scalar(select(func.count(Feedback.id))) or 0
        if total == 0:
            return {
                "total_feedback": 0,
                "helpful_count": 0,
                "not_helpful_count": 0,
                "helpful_percentage": 0.0,
                "average_rating": None,
                "type_breakdown": {},
            }

        helpful_count = self.db.scalar(
            select(func.count(Feedback.id)).where(Feedback.feedback_type == "HELPFUL")
        ) or 0

        not_helpful_count = self.db.scalar(
            select(func.count(Feedback.id)).where(Feedback.feedback_type == "NOT_HELPFUL")
        ) or 0

        helpful_pct = round((helpful_count / total) * 100.0, 1)

        # Average rating across entries where rating was provided
        avg_rating_val = self.db.scalar(
            select(func.avg(Feedback.rating)).where(Feedback.rating.isnot(None))
        )
        avg_rating = round(float(avg_rating_val), 1) if avg_rating_val is not None else None

        # Breakdown by feedback_type
        type_stmt = (
            select(Feedback.feedback_type, func.count(Feedback.id))
            .group_by(Feedback.feedback_type)
        )
        type_rows = self.db.execute(type_stmt).all()
        type_breakdown = {row[0]: row[1] for row in type_rows}

        return {
            "total_feedback": total,
            "helpful_count": helpful_count,
            "not_helpful_count": not_helpful_count,
            "helpful_percentage": helpful_pct,
            "average_rating": avg_rating,
            "type_breakdown": type_breakdown,
        }

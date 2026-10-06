"""EcoSort AI - User Feedback Service (Stage 5).

Handles business logic and validation for submitting user feedback and satisfaction ratings.
"""

import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import Feedback
from app.repositories.classification_repository import ClassificationRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

logger = logging.getLogger("ecosort.feedback")


class FeedbackService:
    """Service managing user feedback processing and validation."""

    def __init__(self, db: Session):
        self.db = db
        self.classification_repo = ClassificationRepository(db)
        self.feedback_repo = FeedbackRepository(db)

    def submit_feedback(self, payload: FeedbackCreate) -> FeedbackResponse:
        """Validates and persists user feedback.
        
        Rules:
        1. Referenced classification request_id must exist in database.
        2. Prevent duplicate feedback submissions for the same request_id (409 Conflict).
        3. Strict rating boundaries (1 to 5) validated by schema.
        """
        # Verify classification record exists
        record = self.classification_repo.get_by_request_id(payload.request_id)
        if not record:
            logger.warning(f"Feedback rejected: request_id={payload.request_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Classification record with request ID '{payload.request_id}' not found.",
            )

        # Check for duplicate submission
        existing = self.feedback_repo.get_by_request_id(payload.request_id)
        if existing:
            logger.info(f"Feedback conflict: duplicate submission for request_id={payload.request_id}.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Feedback has already been submitted for request ID '{payload.request_id}'.",
            )

        feedback_model = Feedback(
            request_id=payload.request_id,
            rating=payload.rating,
            feedback_type=payload.feedback_type.value,
            comment=payload.comment,
        )

        saved = self.feedback_repo.create(feedback_model)
        logger.info(f"Feedback successfully recorded for request_id={payload.request_id}")

        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback.",
            request_id=saved.request_id,
            created_at=saved.created_at,
        )

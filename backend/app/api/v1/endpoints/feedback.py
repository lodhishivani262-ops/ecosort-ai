"""EcoSort AI - Feedback Endpoints (Stage 5).

Allows anonymous users to submit feedback and ratings for previous classification results.
Protected with rate limiting and input sanitization to prevent spam.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.rate_limit import limiter
from app.db.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter()


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit user feedback on a classification result",
    description=(
        "Submits helpfulness feedback, issue tags, and an optional 1-5 rating "
        "linked to a previous classification request_id."
    ),
)
@limiter.limit("20/minute")
def submit_feedback(
    request: Request,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Submits and validates user feedback."""
    service = FeedbackService(db)
    return service.submit_feedback(payload)

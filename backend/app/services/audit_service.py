"""EcoSort AI - Audit & Classification Service (Stage 5).

Provides resilient logging of classification events and safe anonymous history retrieval.
CRITICAL RESILIENCE: Database failures during classification audit recording NEVER crash
or interrupt the user's waste classification response.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import ClassificationRecord
from app.repositories.classification_repository import ClassificationRepository
from app.schemas.classification import (
    ClassificationResultResponse,
    InputType,
    WastePerception,
    WasteRecommendation,
)
from app.schemas.history import ClassificationHistoryItem, HistoryResponse

logger = logging.getLogger("ecosort.audit")


class AuditService:
    """Service orchestrating audit logging and history management."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ClassificationRepository(db)

    def record_classification_resilient(
        self,
        request_id: str,
        input_type: InputType,
        perception: WastePerception,
        recommendation: WasteRecommendation,
        processing_time_ms: int,
        session_id: Optional[str] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
    ) -> Optional[ClassificationRecord]:
        """Resiliently records a classification event into the database.
        
        If the database connection is interrupted or write fails:
        1. Catches the exception safely.
        2. Logs the failure internally for diagnostics.
        3. Returns None without raising an exception to the user.
        """
        try:
            record = ClassificationRecord(
                request_id=request_id,
                session_id=session_id,
                input_type=input_type.value if hasattr(input_type, "value") else str(input_type),
                item_name=perception.item_name,
                material=perception.material,
                condition=perception.condition,
                contamination=(
                    perception.contamination.value
                    if hasattr(perception.contamination, "value")
                    else str(perception.contamination)
                ),
                ai_confidence=(
                    perception.confidence.value
                    if hasattr(perception.confidence, "value")
                    else str(perception.confidence)
                ),
                category=(
                    recommendation.category.value
                    if hasattr(recommendation.category, "value")
                    else str(recommendation.category)
                ),
                recommendation_confidence=(
                    recommendation.confidence.value
                    if hasattr(recommendation.confidence, "value")
                    else str(recommendation.confidence)
                ),
                warning_count=len(recommendation.warnings),
                processing_time_ms=processing_time_ms,
                status=status,
                error_message=error_message,
            )
            return self.repository.create(record)
        except Exception as exc:
            logger.error(
                f"Resilient DB logging failed for request_id={request_id}: {exc}",
                exc_info=False,
            )
            return None

    def get_session_history(
        self, session_id: str, limit: int = 20, offset: int = 0
    ) -> HistoryResponse:
        """Retrieves past classifications belonging exclusively to the specified anonymous session."""
        if not session_id or not session_id.strip():
            return HistoryResponse(session_id=None, total=0, items=[])

        total = self.repository.count_by_session_id(session_id)
        records = self.repository.get_by_session_id(session_id, limit=limit, offset=offset)

        items = [
            ClassificationHistoryItem(
                request_id=r.request_id,
                created_at=r.created_at,
                input_type=r.input_type,
                item_name=r.item_name,
                material=r.material,
                condition=r.condition,
                contamination=r.contamination,
                ai_confidence=r.ai_confidence,
                category=r.category,
                recommendation_confidence=r.recommendation_confidence,
                warning_count=r.warning_count,
                processing_time_ms=r.processing_time_ms,
                status=r.status,
            )
            for r in records
        ]

        return HistoryResponse(
            session_id=session_id,
            total=total,
            items=items,
        )

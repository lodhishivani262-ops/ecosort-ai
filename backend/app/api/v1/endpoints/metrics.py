"""EcoSort AI - Aggregated Metrics Endpoints (Stage 5).

Provides high-level system metrics and category distributions.
INTERNAL/ADMIN NOTICE: In public production deployments, access should be restricted
via METRICS_API_KEY or network perimeter policies.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.schemas.metrics import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter()


@router.get(
    "",
    response_model=MetricsResponse,
    summary="Get aggregated application and categorization metrics",
    description=(
        "Returns aggregated operational statistics: total counts, success rates, "
        "category distribution, and helpfulness metrics. Zero individual user records exposed."
    ),
)
def get_aggregated_metrics(
    db: Session = Depends(get_db),
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key"),
) -> MetricsResponse:
    """Retrieves aggregated performance and feedback metrics."""
    if settings.METRICS_API_KEY and settings.METRICS_API_KEY.strip():
        if x_admin_api_key != settings.METRICS_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized access to internal metrics endpoint.",
            )

    service = MetricsService(db)
    return service.get_metrics()

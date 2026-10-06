"""EcoSort AI - Health Check Endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Schema for health status probe."""

    status: str = Field(default="healthy", examples=["healthy"])
    service: str = Field(default="ecosort-ai-backend", examples=["ecosort-ai-backend"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check probe",
    description="Lightweight health probe indicating backend availability. Does not invoke external AI APIs.",
    tags=["System"],
)
async def get_health() -> HealthCheckResponse:
    """Returns 200 OK if service is running."""
    return HealthCheckResponse(status="healthy", service="ecosort-ai-backend")

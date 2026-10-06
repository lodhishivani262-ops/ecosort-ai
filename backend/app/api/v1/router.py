"""EcoSort AI - API Version 1 Central Router."""

from fastapi import APIRouter
from app.api.v1.endpoints import classify, feedback, health, history, metrics

api_v1_router = APIRouter()

# Include version 1 endpoints
api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(classify.router, tags=["Classification"])
api_v1_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_v1_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_v1_router.include_router(history.router, prefix="/history", tags=["History"])

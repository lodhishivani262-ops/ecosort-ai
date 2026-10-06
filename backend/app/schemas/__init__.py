"""Pydantic schemas and serialization models."""

from app.schemas.classification import (
    ClassificationResponse,
    ClassificationResultResponse,
    ConfidenceLevel,
    ContaminationLevel,
    InputType,
    PerceptionResponse,
    TextClassificationRequest,
    WasteCategory,
    WastePerception,
    WasteRecommendation,
)
from app.schemas.common import ErrorDetail, ErrorResponse, StandardResponse
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackType
from app.schemas.history import ClassificationHistoryItem, HistoryResponse
from app.schemas.metrics import CategoryBreakdown, FeedbackMetrics, MetricsResponse

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "StandardResponse",
    "WasteCategory",
    "ConfidenceLevel",
    "ContaminationLevel",
    "InputType",
    "TextClassificationRequest",
    "WastePerception",
    "WasteRecommendation",
    "ClassificationResultResponse",
    "ClassificationResponse",
    "PerceptionResponse",
    "FeedbackType",
    "FeedbackCreate",
    "FeedbackResponse",
    "CategoryBreakdown",
    "FeedbackMetrics",
    "MetricsResponse",
    "ClassificationHistoryItem",
    "HistoryResponse",
]

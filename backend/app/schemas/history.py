"""EcoSort AI - Anonymous Session History Schemas (Stage 5).

STRICT PRIVACY: Enforces anonymous, session-isolated retrieval of past classifications.
No public discovery of other users' records.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ClassificationHistoryItem(BaseModel):
    """Safe, summarized representation of a past classification record."""

    request_id: str = Field(..., description="Unique request tracing ID")
    created_at: datetime = Field(..., description="Timestamp of classification")
    input_type: str = Field(..., description="Input modality (IMAGE or TEXT)")
    item_name: str = Field(..., description="Identified item name")
    material: str = Field(..., description="Identified physical material")
    condition: str = Field(..., description="Observed cleanliness or state")
    contamination: str = Field(..., description="Contamination degree")
    ai_confidence: str = Field(..., description="Perception confidence indicator")
    category: str = Field(..., description="Determined waste category")
    recommendation_confidence: str = Field(..., description="Recommendation confidence level")
    warning_count: int = Field(..., description="Number of safety/handling warnings issued")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    status: str = Field(..., description="Classification status (SUCCESS / FAILED)")


class HistoryResponse(BaseModel):
    """Response envelope for session-scoped history retrieval."""

    session_id: Optional[str] = Field(None, description="The session ID queried")
    total: int = Field(..., description="Total records found for this session")
    items: List[ClassificationHistoryItem] = Field(
        default_factory=list,
        description="List of past classification summaries for the specified session",
    )

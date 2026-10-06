"""EcoSort AI - Waste Perception and Classification Schemas (Stage 4)."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class WasteCategory(str, Enum):
    """Standardized general household waste segregation categories."""

    ORGANIC = "ORGANIC / WET WASTE"
    DRY_WASTE = "DRY WASTE"
    RECYCLABLE = "RECYCLABLE"
    E_WASTE = "E-WASTE"
    HAZARDOUS = "HAZARDOUS / SPECIAL HANDLING"
    GLASS = "GLASS"
    SANITARY = "SANITARY WASTE"
    UNKNOWN = "UNKNOWN / UNCLASSIFIED"


class ConfidenceLevel(str, Enum):
    """Controlled, un-hallucinated confidence indicator."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ContaminationLevel(str, Enum):
    """Controlled representation of observed or inferred contamination."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class InputType(str, Enum):
    """Input channel modality."""

    IMAGE = "IMAGE"
    TEXT = "TEXT"


class TextClassificationRequest(BaseModel):
    """Validation schema for incoming text classification queries."""

    text: str = Field(
        ...,
        description="Text description of the household waste item",
        examples=["used plastic takeaway food container"],
    )

    @field_validator("text", mode="before")
    @classmethod
    def validate_and_strip_text(cls, v: str) -> str:
        """Sanitizes text input, removing extraneous whitespaces and rejecting empty values."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Text query cannot be empty or contain only whitespace.")
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Text query must be at least 2 characters long.")
        if len(cleaned) > 500:
            raise ValueError("Text query cannot exceed 500 characters.")
        return cleaned


class WastePerception(BaseModel):
    """Structured AI perception output describing what is observed in image or text."""

    item_name: str = Field(
        ...,
        description="Common identifiable name of the waste item",
    )
    material: str = Field(
        ...,
        description="Identified base physical material (e.g., plastic, cardboard, aluminum, glass, organic, unknown)",
    )
    condition: str = Field(
        ...,
        description="Observed physical state or cleanliness (e.g., clean, used, dirty, wet, dry, food-contaminated, broken, unknown)",
    )
    contamination: ContaminationLevel = Field(
        default=ContaminationLevel.UNKNOWN,
        description="Level of observed or inferred contamination (NONE, LOW, MEDIUM, HIGH, UNKNOWN)",
    )
    visual_clues: List[str] = Field(
        default_factory=list,
        description="Short evidence-based visual or descriptive clues (empty for text if none)",
    )
    confidence: ConfidenceLevel = Field(
        ...,
        description="Controlled confidence assessment (HIGH, MEDIUM, LOW)",
    )
    uncertainty_reason: Optional[str] = Field(
        default=None,
        description="Explicit explanation when confidence is LOW or features are ambiguous (null when clear)",
    )
    is_safety_sensitive: bool = Field(
        default=False,
        description="Flags potentially safety-sensitive items (batteries, chemicals, medical sharps, aerosol cans, broken glass)",
    )


class WasteRecommendation(BaseModel):
    """Deterministic, actionable disposal recommendation produced by the EcoSort Rule Engine."""

    category: WasteCategory = Field(
        ...,
        description="Determined waste segregation category",
        examples=[WasteCategory.RECYCLABLE],
    )
    preparation_steps: List[str] = Field(
        default_factory=list,
        description="Actionable preparation steps before disposal (e.g. empty, rinse, dry, separate)",
        examples=[["Empty remaining contents", "Rinse off food residue", "Allow to air-dry"]],
    )
    disposal_guidance: str = Field(
        ...,
        description="General disposal route recommendation",
        examples=["Place in standard dry recycling stream after preparation."],
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Safety warnings, contamination alerts, or municipal caveats",
        examples=[["Follow your local waste authority's guidelines."]],
    )
    confidence: ConfidenceLevel = Field(
        ...,
        description="Recommendation confidence level (never elevated beyond perception confidence)",
        examples=[ConfidenceLevel.HIGH],
    )
    reason: str = Field(
        ...,
        description="Deterministic explainable reason formulating this recommendation",
        examples=["Clean plastic beverage container is eligible for standard mechanical recycling."],
    )
    uncertainty_reason: Optional[str] = Field(
        default=None,
        description="Explanation when recommendation is uncertain or conservative",
        examples=[None],
    )


class ClassificationResultResponse(BaseModel):
    """Complete API response combining AI perception with deterministic rule recommendation."""

    request_id: str = Field(
        ...,
        description="Unique request tracing identifier",
        examples=["b79b29cb-69b2-4d57-9d7a-cf6e0be5b8a1"],
    )
    input_type: InputType = Field(
        ...,
        description="Modality of the input processed (IMAGE or TEXT)",
        examples=[InputType.IMAGE],
    )
    perception: WastePerception = Field(
        ...,
        description="Detailed perception observation generated by the AI service",
    )
    recommendation: WasteRecommendation = Field(
        ...,
        description="Actionable disposal guidance generated by the deterministic rule engine",
    )
    mock: bool = Field(
        default=False,
        description="Indicates whether the response used mock AI perception",
    )


# Backward-compatible aliases
ClassificationResponse = ClassificationResultResponse
PerceptionResponse = ClassificationResultResponse

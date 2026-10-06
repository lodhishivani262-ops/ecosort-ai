"""Unit tests for the Gemini AI Perception Service and Error Handling (Stage 3).

Verifies all 12 perception scenarios without requiring a live Gemini API key.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.genai import errors as genai_errors

from app.core.security import AppException
from app.schemas.classification import (
    ConfidenceLevel,
    ContaminationLevel,
    WastePerception,
)
from app.services.ai_service import GeminiAIService


class MockGeminiResponse:
    """Mock object simulating Google GenAI response."""

    def __init__(self, text: str):
        self.text = text


@pytest.fixture
def mock_genai_client():
    """Provides a mocked google-genai client with async models."""
    client = MagicMock()
    client.aio = MagicMock()
    client.aio.models = MagicMock()
    return client


# ------------------------------------------------------------------------------
# Test 1: Valid image -> structured perception
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_valid_image_perception(mock_genai_client):
    payload = {
        "item_name": "plastic water bottle",
        "material": "plastic (PET-1)",
        "condition": "empty and dry",
        "contamination": "LOW",
        "visual_clues": ["transparent cylindrical body", "plastic screw cap attached"],
        "confidence": "HIGH",
        "uncertainty_reason": None,
        "is_safety_sensitive": False,
    }
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse(json.dumps(payload))
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        client=mock_genai_client,
    )
    result = await service.analyze_image(b"\xff\xd8\xff...", "bottle.jpg", "image/jpeg")

    assert isinstance(result, WastePerception)
    assert result.item_name == "plastic water bottle"
    assert result.material == "plastic (PET-1)"
    assert result.confidence == ConfidenceLevel.HIGH
    assert result.contamination == ContaminationLevel.LOW
    assert result.is_safety_sensitive is False
    assert len(result.visual_clues) == 2


# ------------------------------------------------------------------------------
# Test 2: Valid text -> structured perception
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_valid_text_perception(mock_genai_client):
    payload = {
        "item_name": "greasy takeaway food box",
        "material": "corrugated cardboard",
        "condition": "food-contaminated",
        "contamination": "HIGH",
        "visual_clues": [],
        "confidence": "HIGH",
        "uncertainty_reason": None,
        "is_safety_sensitive": False,
    }
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse(json.dumps(payload))
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        client=mock_genai_client,
    )
    result = await service.analyze_text("greasy takeaway food box")

    assert result.item_name == "greasy takeaway food box"
    assert result.contamination == ContaminationLevel.HIGH
    assert result.confidence == ConfidenceLevel.HIGH


# ------------------------------------------------------------------------------
# Test 3: Low-confidence response with uncertainty reason
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_low_confidence_perception(mock_genai_client):
    payload = {
        "item_name": "unidentified object",
        "material": "unknown",
        "condition": "unknown",
        "contamination": "UNKNOWN",
        "visual_clues": ["blurry silhouette"],
        "confidence": "LOW",
        "uncertainty_reason": "Image is excessively blurry and partially occluded.",
        "is_safety_sensitive": False,
    }
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse(json.dumps(payload))
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        client=mock_genai_client,
    )
    result = await service.analyze_image(b"fake", "blurry.jpg")

    assert result.confidence == ConfidenceLevel.LOW
    assert result.uncertainty_reason == "Image is excessively blurry and partially occluded."


# ------------------------------------------------------------------------------
# Test 4: Unknown material handling
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_unknown_material_perception(mock_genai_client):
    payload = {
        "item_name": "composite scrap",
        "material": "unknown",
        "condition": "used",
        "contamination": "LOW",
        "visual_clues": ["foil-like coating", "cardboard layer"],
        "confidence": "MEDIUM",
        "uncertainty_reason": "Multi-layer laminate material cannot be identified with certainty.",
        "is_safety_sensitive": False,
    }
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse(json.dumps(payload))
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        client=mock_genai_client,
    )
    result = await service.analyze_text("weird shiny wrapper")

    assert result.material == "unknown"


# ------------------------------------------------------------------------------
# Test 5: Unknown condition handling
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_unknown_condition_perception(mock_genai_client):
    payload = {
        "item_name": "metal aerosol can",
        "material": "aluminum",
        "condition": "unknown",
        "contamination": "UNKNOWN",
        "visual_clues": ["sealed canister", "warning symbols"],
        "confidence": "HIGH",
        "uncertainty_reason": None,
        "is_safety_sensitive": True,
    }
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse(json.dumps(payload))
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        client=mock_genai_client,
    )
    result = await service.analyze_text("aerosol spray can")

    assert result.condition == "unknown"
    assert result.is_safety_sensitive is True


# ------------------------------------------------------------------------------
# Test 6: Malformed AI response handling
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_malformed_ai_response(mock_genai_client):
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse("{malformed json text without closing")
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        max_retries=0,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("some trash")

    assert exc_info.value.code == "AI_PARSING_ERROR"
    assert exc_info.value.status_code == 502


# ------------------------------------------------------------------------------
# Test 7: Provider timeout handling
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_provider_timeout_handling(mock_genai_client):
    async def delayed_call(*args, **kwargs):
        await asyncio.sleep(2.0)
        return MockGeminiResponse("{}")

    mock_genai_client.aio.models.generate_content = AsyncMock(side_effect=delayed_call)

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        timeout_seconds=0.1,  # Short timeout for test
        max_retries=0,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    assert exc_info.value.code == "AI_TIMEOUT"
    assert exc_info.value.status_code == 504


# ------------------------------------------------------------------------------
# Test 8: Provider unavailable (5xx error)
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_provider_unavailable_handling(mock_genai_client):
    # Simulate upstream 503 ServerError
    server_error = genai_errors.APIError(503, "Service Unavailable")
    mock_genai_client.aio.models.generate_content = AsyncMock(side_effect=server_error)

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        max_retries=1,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    assert exc_info.value.code == "AI_SERVICE_UNAVAILABLE"
    assert exc_info.value.status_code == 503


# ------------------------------------------------------------------------------
# Test 9: Missing API key handling
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_missing_api_key_handling():
    service = GeminiAIService(api_key=None, client=None)
    # Ensure api_key is None or empty
    service.api_key = ""

    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    assert exc_info.value.code == "AI_API_KEY_MISSING"
    assert exc_info.value.status_code == 503


# ------------------------------------------------------------------------------
# Test 10: AI Provider Auth Error (401/403 Invalid API key)
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_provider_auth_error_handling(mock_genai_client):
    auth_error = genai_errors.APIError(403, "API_KEY_INVALID: The provided API key is invalid.")
    mock_genai_client.aio.models.generate_content = AsyncMock(side_effect=auth_error)

    service = GeminiAIService(
        api_key="bad-key",
        model_name="test-model",
        max_retries=0,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    assert exc_info.value.code == "AI_AUTH_FAILED"
    assert exc_info.value.status_code == 502


# ------------------------------------------------------------------------------
# Test 11 & 12: Verify NO Final Disposal Recommendation Is Produced
# ------------------------------------------------------------------------------
def test_perception_model_excludes_disposal_rules():
    """Verify that WastePerception adheres strictly to perception and contains NO disposal rules."""
    perception = WastePerception(
        item_name="AA battery",
        material="lithium/metal",
        condition="used",
        contamination=ContaminationLevel.NONE,
        visual_clues=["cylindrical metal cell"],
        confidence=ConfidenceLevel.HIGH,
        uncertainty_reason=None,
        is_safety_sensitive=True,
    )

    dumped = perception.model_dump()

    # Assert architectural boundaries
    forbidden_keys = [
        "category",
        "disposal_method",
        "disposal_recommendation",
        "bin",
        "target_bin",
        "preparation_steps",
        "action_steps",
    ]
    for key in forbidden_keys:
        assert key not in dumped, f"Architectural violation: {key} should NOT be in perception layer"


# ------------------------------------------------------------------------------
# Test 13: Empty AI Response Handling
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_empty_ai_response_handling(mock_genai_client):
    mock_genai_client.aio.models.generate_content = AsyncMock(
        return_value=MockGeminiResponse("")
    )

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        max_retries=0,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    assert exc_info.value.code == "AI_EMPTY_RESPONSE"
    assert exc_info.value.status_code == 502


# ------------------------------------------------------------------------------
# Test 14: Provider Rate Limiting (429)
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_provider_rate_limited_handling(mock_genai_client):
    rate_limit_err = genai_errors.APIError(429, "RESOURCE_EXHAUSTED: Quota exceeded.")
    mock_genai_client.aio.models.generate_content = AsyncMock(side_effect=rate_limit_err)

    service = GeminiAIService(
        api_key="test-api-key",
        model_name="test-model",
        max_retries=0,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    assert exc_info.value.code == "AI_RATE_LIMITED"
    assert exc_info.value.status_code == 429


# ------------------------------------------------------------------------------
# Test 15: Secret/Key Leakage Prevention in Errors
# ------------------------------------------------------------------------------
@pytest.mark.anyio
async def test_api_key_not_leaked_in_exceptions(mock_genai_client):
    secret_key = "AIzaSySUPER_SECRET_KEY_12345"
    mock_genai_client.aio.models.generate_content = AsyncMock(
        side_effect=genai_errors.APIError(500, f"Internal error involving {secret_key}")
    )

    service = GeminiAIService(
        api_key=secret_key,
        model_name="test-model",
        max_retries=0,
        client=mock_genai_client,
    )
    with pytest.raises(AppException) as exc_info:
        await service.analyze_text("test item")

    # Verify that the user-facing exception does NOT expose the API key
    assert secret_key not in exc_info.value.message


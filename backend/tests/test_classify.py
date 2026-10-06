"""Integration Tests for Waste Classification & Recommendation API (Stage 4)."""

import pytest
from fastapi.testclient import TestClient


def test_classify_valid_text_json(client: TestClient):
    """Test valid text query on unified endpoint returning perception + recommendation."""
    response = client.post(
        "/api/v1/classify",
        json={"text": "used plastic water bottle"},
    )
    assert response.status_code == 200
    data = response.json()

    # Verify top-level structure
    assert "request_id" in data
    assert data["input_type"] == "TEXT"
    assert "perception" in data
    assert "recommendation" in data

    # Verify perception attributes
    p = data["perception"]
    assert "item_name" in p
    assert "material" in p
    assert "condition" in p
    assert "contamination" in p
    assert "confidence" in p

    # Verify recommendation attributes
    r = data["recommendation"]
    assert "category" in r
    assert "preparation_steps" in r
    assert "disposal_guidance" in r
    assert "warnings" in r
    assert "confidence" in r
    assert "reason" in r
    assert r["category"] == "RECYCLABLE"
    assert len(r["preparation_steps"]) > 0


def test_classify_safety_sensitive_item(client: TestClient):
    """Test that safety-sensitive items trigger safety override in recommendation."""
    response = client.post(
        "/api/v1/classify",
        json={"text": "lithium ion laptop battery cell"},
    )
    assert response.status_code == 200
    data = response.json()

    p = data["perception"]
    r = data["recommendation"]

    assert p["is_safety_sensitive"] is True
    # Recommendation category must be HAZARDOUS / SPECIAL HANDLING, overriding ordinary recycling
    assert r["category"] == "HAZARDOUS / SPECIAL HANDLING"
    assert any("fire" in w.lower() for w in r["warnings"])
    assert any("tape" in s.lower() for s in r["preparation_steps"])


def test_classify_empty_text_rejection(client: TestClient):
    """Test that empty or whitespace-only text queries are rejected with 400."""
    response = client.post("/api/v1/classify", json={"text": ""})
    assert response.status_code == 400
    err = response.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "empty" in err["message"].lower()

    # Test whitespace-only text
    response_ws = client.post("/api/v1/classify", json={"text": "     "})
    assert response_ws.status_code == 400
    err_ws = response_ws.json()["error"]
    assert err_ws["code"] == "VALIDATION_ERROR"


def test_classify_too_long_text_rejection(client: TestClient):
    """Test that overly long text queries (>500 chars) are rejected with 400."""
    response = client.post("/api/v1/classify", json={"text": "a" * 501})
    assert response.status_code == 400
    err = response.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"


def test_classify_valid_image(client: TestClient, valid_jpeg: bytes):
    """Test valid image upload via multipart/form-data on unified endpoint."""
    response = client.post(
        "/api/v1/classify",
        files={"file": ("water_bottle.jpg", valid_jpeg, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["input_type"] == "IMAGE"
    assert "perception" in data
    assert "recommendation" in data
    r = data["recommendation"]
    assert r["category"] == "RECYCLABLE"
    assert len(r["preparation_steps"]) > 0


def test_classify_unsupported_file_rejection(client: TestClient):
    """Test that unsupported text/pdf files are rejected with 415."""
    response = client.post(
        "/api/v1/classify",
        files={"file": ("document.txt", b"Hello World", "text/plain")},
    )
    assert response.status_code == 415
    data = response.json()
    assert data["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_classify_oversized_image_rejection(client: TestClient, oversized_image: bytes):
    """Test that files exceeding 5MB are rejected with 413 Payload Too Large."""
    response = client.post(
        "/api/v1/classify",
        files={"file": ("huge_photo.jpg", oversized_image, "image/jpeg")},
    )
    assert response.status_code == 413
    data = response.json()
    assert data["error"]["code"] == "FILE_TOO_LARGE"


def test_classify_disguised_executable_rejection(client: TestClient, disguised_exe: bytes):
    """Test that an executable file renamed to .jpg is rejected via magic byte inspection."""
    response = client.post(
        "/api/v1/classify",
        files={"file": ("malicious_payload.jpg", disguised_exe, "image/jpeg")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_FILE_TYPE"


def test_classify_malformed_json_rejection(client: TestClient):
    """Test that malformed JSON strings are rejected with 400 INVALID_JSON."""
    response = client.post(
        "/api/v1/classify",
        content=b'{"text": "broken json...',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_JSON"


def test_classify_missing_input_rejection(client: TestClient):
    """Test that an empty multipart form with neither file nor text is rejected."""
    response = client.post(
        "/api/v1/classify",
        data={},
        headers={"Content-Type": "multipart/form-data; boundary=boundary123"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] in ["MISSING_INPUT", "INVALID_FORM"]


def test_dedicated_endpoints(client: TestClient, valid_png: bytes):
    """Test dedicated /classify/text and /classify/image endpoints."""
    # Dedicated text
    res_text = client.post("/api/v1/classify/text", json={"text": "lithium battery"})
    assert res_text.status_code == 200
    assert res_text.json()["recommendation"]["category"] == "HAZARDOUS / SPECIAL HANDLING"

    # Dedicated image
    res_img = client.post(
        "/api/v1/classify/image",
        files={"file": ("item.png", valid_png, "image/png")},
    )
    assert res_img.status_code == 200
    assert res_img.json()["input_type"] == "IMAGE"
    assert res_img.json()["recommendation"]["category"] == "RECYCLABLE"


def test_request_id_propagation(client: TestClient):
    """Test that Request ID is propagated between headers and body."""
    custom_id = "test-custom-request-id-12345"
    response = client.post(
        "/api/v1/classify",
        json={"text": "glass bottle"},
        headers={"X-Request-ID": custom_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == custom_id
    assert response.headers.get("x-request-id") == custom_id


def test_rate_limiting_behavior(client: TestClient):
    """Test that making rapid requests past the configured limit triggers HTTP 429."""
    responses = []
    for _ in range(25):
        res = client.post("/api/v1/classify", json={"text": "soda can"})
        responses.append(res.status_code)

    assert 429 in responses
    last_429 = [r for r in responses if r == 429]
    assert len(last_429) > 0


def test_classify_valid_webp(client: TestClient, valid_webp: bytes):
    """Test valid WebP image upload via multipart/form-data."""
    response = client.post(
        "/api/v1/classify",
        files={"file": ("photo.webp", valid_webp, "image/webp")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input_type"] == "IMAGE"
    assert "perception" in data
    assert "recommendation" in data


def test_classify_empty_json_body(client: TestClient):
    """Test that an empty request body with application/json header is rejected."""
    response = client.post(
        "/api/v1/classify",
        content=b"",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "MISSING_INPUT"


def test_classify_json_array_instead_of_object(client: TestClient):
    """Test that a JSON list is rejected as invalid payload."""
    response = client.post(
        "/api/v1/classify",
        content=b'[{"text": "plastic bottle"}]',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_JSON"


def test_classify_unsupported_http_method(client: TestClient):
    """Test that GET on /api/v1/classify returns 405 Method Not Allowed."""
    response = client.get("/api/v1/classify")
    assert response.status_code == 405
    data = response.json()
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_classify_database_resilience(client: TestClient):
    """Test that database audit logging failure does NOT prevent the classification result."""
    from unittest.mock import patch

    with patch("app.services.audit_service.AuditService.record_classification_resilient") as mock_audit:
        mock_audit.side_effect = Exception("Simulated DB connection crash")
        response = client.post(
            "/api/v1/classify",
            json={"text": "clean aluminum can"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["perception"]["item_name"] is not None
        assert data["recommendation"]["category"] == "RECYCLABLE"


def test_classify_ai_service_timeout(client: TestClient):
    """Test that AI timeout is translated to clean HTTP 504 error response."""
    from unittest.mock import AsyncMock
    from app.core.security import AppException
    from app.services.ai_service import get_ai_service
    from app.main import app

    failing_service = AsyncMock()
    failing_service.analyze_text.side_effect = AppException(
        code="AI_TIMEOUT",
        message="AI perception service timed out after 20 seconds.",
        status_code=504,
    )
    app.dependency_overrides[get_ai_service] = lambda: failing_service

    try:
        response = client.post("/api/v1/classify", json={"text": "soda can"})
        assert response.status_code == 504
        data = response.json()
        assert data["error"]["code"] == "AI_TIMEOUT"
        assert "timed out" in data["error"]["message"].lower()
    finally:
        from app.services.ai_service import MockAIService
        app.dependency_overrides[get_ai_service] = lambda: MockAIService()


def test_classify_ai_service_unavailable(client: TestClient):
    """Test that AI service unavailability returns HTTP 503 error."""
    from unittest.mock import AsyncMock
    from app.core.security import AppException
    from app.services.ai_service import get_ai_service
    from app.main import app

    failing_service = AsyncMock()
    failing_service.analyze_text.side_effect = AppException(
        code="AI_SERVICE_UNAVAILABLE",
        message="The AI service is temporarily unavailable. Please try again.",
        status_code=503,
    )
    app.dependency_overrides[get_ai_service] = lambda: failing_service

    try:
        response = client.post("/api/v1/classify", json={"text": "cardboard box"})
        assert response.status_code == 503
        data = response.json()
        assert data["error"]["code"] == "AI_SERVICE_UNAVAILABLE"
    finally:
        from app.services.ai_service import MockAIService
        app.dependency_overrides[get_ai_service] = lambda: MockAIService()


def test_classify_ai_service_parsing_error(client: TestClient):
    """Test that AI parsing failure returns HTTP 502 Bad Gateway."""
    from unittest.mock import AsyncMock
    from app.core.security import AppException
    from app.services.ai_service import get_ai_service
    from app.main import app

    failing_service = AsyncMock()
    failing_service.analyze_text.side_effect = AppException(
        code="AI_PARSING_ERROR",
        message="Failed to parse structured observation from AI response.",
        status_code=502,
    )
    app.dependency_overrides[get_ai_service] = lambda: failing_service

    try:
        response = client.post("/api/v1/classify", json={"text": "glass jar"})
        assert response.status_code == 502
        data = response.json()
        assert data["error"]["code"] == "AI_PARSING_ERROR"
    finally:
        from app.services.ai_service import MockAIService
        app.dependency_overrides[get_ai_service] = lambda: MockAIService()


def test_classify_unknown_material_low_confidence(client: TestClient):
    """Test classifying ambiguous/unknown item returns UNKNOWN category and low confidence."""
    response = client.post(
        "/api/v1/classify",
        json={"text": "blurry weird unknown object with strange texture"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["recommendation"]["category"] == "UNKNOWN / UNCLASSIFIED"
    assert data["recommendation"]["confidence"] == "LOW"
    assert "uncertain" in data["recommendation"]["warnings"][0].lower()


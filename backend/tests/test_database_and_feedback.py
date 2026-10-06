"""EcoSort AI - Database, History & Feedback Test Suite (Stage 5).

Verifies the 15 mandated testing requirements:
1. Database connection probe
2. Classification record persistence
3. Classification record retrieval
4. Successful user feedback submission
5. Strict rating range validation (rejects 0, negative, > 5)
6. Invalid feedback type rejection
7. Excessively long comment rejection (> 500 characters)
8. Missing request ID rejection
9. Database transaction rollback on constraint violation
10. Resilient classification execution even when database logging fails
11. Aggregated metrics computation accuracy
12. Clean metrics calculation on an empty database (zero data fabrication)
13. Duplicate feedback prevention (409 Conflict) and non-existent request ID (404 Not Found)
14. API request validation envelopes
15. Rate limiting on the feedback endpoint
16. Anonymous session history isolation (cross-session privacy)
17. Data retention cleanup policy
18. Strict verification that NO image data is persisted in database columns
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.database import check_db_connection
from app.db.models import ClassificationRecord, Feedback
from app.repositories.classification_repository import ClassificationRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.classification import (
    ConfidenceLevel,
    ContaminationLevel,
    InputType,
    WasteCategory,
    WastePerception,
    WasteRecommendation,
)
from app.services.audit_service import AuditService


# ------------------------------------------------------------------------------
# 1. Database Connection Probe
# ------------------------------------------------------------------------------
def test_database_connection():
    """Confirms database connection probe executes successfully."""
    assert check_db_connection() is True


# ------------------------------------------------------------------------------
# 2. Classification Record Creation
# ------------------------------------------------------------------------------
def test_classification_record_creation(db_session: Session):
    """Verifies that a classification record is persisted with structured metadata."""
    repo = ClassificationRepository(db_session)
    record = ClassificationRecord(
        request_id="test-req-001",
        session_id="session-xyz",
        input_type="TEXT",
        item_name="PET bottle",
        material="plastic",
        condition="clean",
        contamination="NONE",
        ai_confidence="HIGH",
        category=WasteCategory.RECYCLABLE.value,
        recommendation_confidence="HIGH",
        warning_count=1,
        processing_time_ms=120,
        status="SUCCESS",
    )
    saved = repo.create(record)
    assert saved.id is not None
    assert saved.request_id == "test-req-001"
    assert saved.category == WasteCategory.RECYCLABLE.value
    assert saved.created_at is not None


# ------------------------------------------------------------------------------
# 3. Classification Record Retrieval
# ------------------------------------------------------------------------------
def test_classification_record_retrieval(db_session: Session):
    """Verifies retrieval by request_id and session_id."""
    repo = ClassificationRepository(db_session)
    record = ClassificationRecord(
        request_id="test-req-002",
        session_id="session-user-1",
        input_type="IMAGE",
        item_name="aluminum can",
        material="aluminum",
        condition="used",
        contamination="LOW",
        ai_confidence="HIGH",
        category=WasteCategory.RECYCLABLE.value,
        recommendation_confidence="HIGH",
        warning_count=0,
        processing_time_ms=250,
        status="SUCCESS",
    )
    repo.create(record)

    found = repo.get_by_request_id("test-req-002")
    assert found is not None
    assert found.item_name == "aluminum can"

    session_records = repo.get_by_session_id("session-user-1")
    assert len(session_records) == 1
    assert session_records[0].request_id == "test-req-002"


# ------------------------------------------------------------------------------
# 4. Feedback Creation
# ------------------------------------------------------------------------------
def test_feedback_creation_success(client: TestClient, db_session: Session):
    """Verifies submitting feedback for an existing classification succeeds."""
    # Seed a classification record
    repo = ClassificationRepository(db_session)
    repo.create(
        ClassificationRecord(
            request_id="fb-test-req-1",
            input_type="TEXT",
            item_name="glass jar",
            material="glass",
            condition="clean",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.GLASS.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=100,
            status="SUCCESS",
        )
    )

    response = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "fb-test-req-1",
            "rating": 5,
            "feedback_type": "HELPFUL",
            "comment": "Accurate advice on washing glass jar.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["request_id"] == "fb-test-req-1"
    assert "Thank you" in data["message"]


# ------------------------------------------------------------------------------
# 5. Invalid Rating Validation (0, negative, > 5)
# ------------------------------------------------------------------------------
@pytest.mark.parametrize("invalid_rating", [0, -1, -5, 6, 10])
def test_feedback_invalid_rating(client: TestClient, invalid_rating: int):
    """Strictly validates rating must be between 1 and 5."""
    response = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "dummy-req-id-1234",
            "rating": invalid_rating,
            "feedback_type": "HELPFUL",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------------------------
# 6. Invalid Feedback Type Validation
# ------------------------------------------------------------------------------
def test_feedback_invalid_type(client: TestClient):
    """Validates feedback_type must be a member of FeedbackType enum."""
    response = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "dummy-req-id-1234",
            "rating": 4,
            "feedback_type": "SUPER_AWESOME",  # Not a valid enum
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------------------------
# 7. Excessively Long Comment Validation
# ------------------------------------------------------------------------------
def test_feedback_excessively_long_comment(client: TestClient):
    """Rejects comments exceeding 500 characters."""
    long_comment = "x" * 501
    response = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "dummy-req-id-1234",
            "rating": 3,
            "feedback_type": "OTHER",
            "comment": long_comment,
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------------------------
# 8. Missing Request ID
# ------------------------------------------------------------------------------
def test_feedback_missing_request_id(client: TestClient):
    """Rejects feedback without a request_id."""
    response = client.post(
        "/api/v1/feedback",
        json={
            "rating": 4,
            "feedback_type": "HELPFUL",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------------------------
# 9. Database Transaction Rollback
# ------------------------------------------------------------------------------
def test_database_transaction_rollback(db_session: Session):
    """Verifies that an error (e.g. duplicate unique request_id) triggers a safe rollback."""
    repo = ClassificationRepository(db_session)
    record1 = ClassificationRecord(
        request_id="unique-tx-req",
        input_type="TEXT",
        item_name="cardboard box",
        material="cardboard",
        condition="dry",
        contamination="NONE",
        ai_confidence="HIGH",
        category=WasteCategory.RECYCLABLE.value,
        recommendation_confidence="HIGH",
        warning_count=0,
        processing_time_ms=80,
        status="SUCCESS",
    )
    repo.create(record1)

    record2 = ClassificationRecord(
        request_id="unique-tx-req",  # Duplicate unique key
        input_type="TEXT",
        item_name="duplicate box",
        material="cardboard",
        condition="dry",
        contamination="NONE",
        ai_confidence="HIGH",
        category=WasteCategory.RECYCLABLE.value,
        recommendation_confidence="HIGH",
        warning_count=0,
        processing_time_ms=80,
        status="SUCCESS",
    )
    with pytest.raises(Exception):
        repo.create(record2)

    # Verify session is still functional after rollback
    count = repo.count_by_session_id("nonexistent")
    assert count == 0


# ------------------------------------------------------------------------------
# 10. Database Failure Handling in Classification Flow (Resilience)
# ------------------------------------------------------------------------------
def test_database_failure_handling_in_classification(client: TestClient):
    """Ensures classification succeeds even if DB persistence encounters an operational error."""
    with patch.object(ClassificationRepository, "create", side_effect=Exception("Database disk full")):
        response = client.post(
            "/api/v1/classify",
            json={"text": "used clean plastic beverage bottle"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["perception"]["item_name"] is not None
        assert data["recommendation"]["category"] == WasteCategory.RECYCLABLE.value


# ------------------------------------------------------------------------------
# 11. Metrics Calculation
# ------------------------------------------------------------------------------
def test_metrics_calculation(client: TestClient, db_session: Session):
    """Verifies accuracy of aggregated metrics calculation."""
    cls_repo = ClassificationRepository(db_session)
    fb_repo = FeedbackRepository(db_session)

    # Seed 3 classifications
    r1 = cls_repo.create(
        ClassificationRecord(
            request_id="m-req-1",
            input_type="TEXT",
            item_name="apple core",
            material="organic",
            condition="fresh",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.ORGANIC.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=100,
            status="SUCCESS",
        )
    )
    r2 = cls_repo.create(
        ClassificationRecord(
            request_id="m-req-2",
            input_type="TEXT",
            item_name="plastic bottle",
            material="plastic",
            condition="clean",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.RECYCLABLE.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=200,
            status="SUCCESS",
        )
    )
    r3 = cls_repo.create(
        ClassificationRecord(
            request_id="m-req-3",
            input_type="TEXT",
            item_name="blurry object",
            material="unknown",
            condition="unknown",
            contamination="UNKNOWN",
            ai_confidence="LOW",
            category=WasteCategory.UNKNOWN.value,
            recommendation_confidence="LOW",
            warning_count=0,
            processing_time_ms=300,
            status="SUCCESS",
        )
    )

    # Seed 2 feedbacks
    fb_repo.create(
        Feedback(
            request_id="m-req-1",
            rating=5,
            feedback_type="HELPFUL",
            comment="Great",
        )
    )
    fb_repo.create(
        Feedback(
            request_id="m-req-2",
            rating=3,
            feedback_type="NOT_HELPFUL",
            comment="Unclear",
        )
    )

    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    metrics = response.json()

    assert metrics["total_classifications"] == 3
    assert metrics["successful_classifications"] == 3
    assert metrics["failed_classifications"] == 0
    assert metrics["average_processing_time_ms"] == 200.0
    assert metrics["low_confidence_percentage"] == 33.3  # 1 out of 3

    # Feedback metrics
    fb = metrics["feedback"]
    assert fb["total_feedback"] == 2
    assert fb["helpful_count"] == 1
    assert fb["not_helpful_count"] == 1
    assert fb["helpful_percentage"] == 50.0
    assert fb["average_rating"] == 4.0  # (5 + 3) / 2


# ------------------------------------------------------------------------------
# 12. Empty Database Metrics (No Fabrication)
# ------------------------------------------------------------------------------
def test_empty_database_metrics(client: TestClient):
    """Verifies clean zero-metric response when no records exist."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_classifications"] == 0
    assert data["successful_classifications"] == 0
    assert data["failed_classifications"] == 0
    assert data["average_processing_time_ms"] == 0.0
    assert data["low_confidence_percentage"] == 0.0
    assert data["categories"] == []
    assert data["feedback"]["total_feedback"] == 0
    assert data["feedback"]["average_rating"] is None


# ------------------------------------------------------------------------------
# 13. Duplicate Feedback and Non-existent Request ID
# ------------------------------------------------------------------------------
def test_feedback_nonexistent_request_id(client: TestClient):
    """Returns 404 when submitting feedback for a non-existent request_id."""
    response = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "nonexistent-req-99999",
            "rating": 4,
            "feedback_type": "HELPFUL",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["error"]["message"].lower()


def test_duplicate_feedback_conflict(client: TestClient, db_session: Session):
    """Returns 409 Conflict when submitting multiple feedback records for same request_id."""
    repo = ClassificationRepository(db_session)
    repo.create(
        ClassificationRecord(
            request_id="dup-test-req-1",
            input_type="TEXT",
            item_name="juice carton",
            material="composite",
            condition="clean",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.DRY_WASTE.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=90,
            status="SUCCESS",
        )
    )

    # First submission -> 201 Created
    res1 = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "dup-test-req-1",
            "rating": 5,
            "feedback_type": "HELPFUL",
        },
    )
    assert res1.status_code == 201

    # Second submission -> 409 Conflict
    res2 = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "dup-test-req-1",
            "rating": 5,
            "feedback_type": "HELPFUL",
        },
    )
    assert res2.status_code == 409
    assert "already been submitted" in res2.json()["error"]["message"].lower()


# ------------------------------------------------------------------------------
# 14. API Validation Tests
# ------------------------------------------------------------------------------
def test_feedback_api_validation(client: TestClient):
    """Tests bad payloads are properly rejected by FastAPI schema validation."""
    # Completely empty body
    res1 = client.post("/api/v1/feedback", json={})
    assert res1.status_code == 400
    assert res1.json()["error"]["code"] == "VALIDATION_ERROR"

    # String rating
    res2 = client.post(
        "/api/v1/feedback",
        json={"request_id": "req-12345678", "rating": "five", "feedback_type": "HELPFUL"},
    )
    assert res2.status_code == 400
    assert res2.json()["error"]["code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------------------------
# 15. Rate Limiting on Feedback
# ------------------------------------------------------------------------------
def test_rate_limiting_on_feedback(client: TestClient, db_session: Session):
    """Tests that feedback endpoint enforces rate limits."""
    repo = ClassificationRepository(db_session)
    repo.create(
        ClassificationRecord(
            request_id="rl-test-req",
            input_type="TEXT",
            item_name="can",
            material="metal",
            condition="clean",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.RECYCLABLE.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=80,
            status="SUCCESS",
        )
    )

    # Send 25 requests rapidly (limit is 20/minute)
    statuses = []
    for _ in range(25):
        resp = client.post(
            "/api/v1/feedback",
            json={
                "request_id": "rl-test-req",
                "rating": 5,
                "feedback_type": "HELPFUL",
            },
        )
        statuses.append(resp.status_code)

    assert 429 in statuses


# ------------------------------------------------------------------------------
# 16. Anonymous Session History Isolation
# ------------------------------------------------------------------------------
def test_anonymous_history_session_isolation(client: TestClient, db_session: Session):
    """Verifies that history queries are strictly scoped to the requesting session ID."""
    repo = ClassificationRepository(db_session)
    repo.create(
        ClassificationRecord(
            request_id="hist-s1-1",
            session_id="session-alice",
            input_type="TEXT",
            item_name="item alice",
            material="plastic",
            condition="clean",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.RECYCLABLE.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=100,
            status="SUCCESS",
        )
    )
    repo.create(
        ClassificationRecord(
            request_id="hist-s2-1",
            session_id="session-bob",
            input_type="TEXT",
            item_name="item bob",
            material="glass",
            condition="clean",
            contamination="NONE",
            ai_confidence="HIGH",
            category=WasteCategory.GLASS.value,
            recommendation_confidence="HIGH",
            warning_count=0,
            processing_time_ms=100,
            status="SUCCESS",
        )
    )

    # Query for session-alice
    res_alice = client.get("/api/v1/history?session_id=session-alice")
    assert res_alice.status_code == 200
    data_alice = res_alice.json()
    assert data_alice["total"] == 1
    assert data_alice["items"][0]["request_id"] == "hist-s1-1"
    assert data_alice["items"][0]["item_name"] == "item alice"

    # Query without session_id returns empty list
    res_none = client.get("/api/v1/history")
    assert res_none.status_code == 200
    assert res_none.json()["total"] == 0
    assert res_none.json()["items"] == []


# ------------------------------------------------------------------------------
# 17. Data Retention Strategy
# ------------------------------------------------------------------------------
def test_data_retention_cleanup(db_session: Session):
    """Verifies deleting records older than N days operates correctly."""
    repo = ClassificationRepository(db_session)
    now = datetime.now(timezone.utc)

    old_record = ClassificationRecord(
        request_id="old-req-1",
        created_at=now - timedelta(days=95),  # 95 days old
        input_type="TEXT",
        item_name="old item",
        material="plastic",
        condition="clean",
        contamination="NONE",
        ai_confidence="HIGH",
        category=WasteCategory.RECYCLABLE.value,
        recommendation_confidence="HIGH",
        warning_count=0,
        processing_time_ms=100,
        status="SUCCESS",
    )
    new_record = ClassificationRecord(
        request_id="new-req-1",
        created_at=now - timedelta(days=5),  # 5 days old
        input_type="TEXT",
        item_name="new item",
        material="plastic",
        condition="clean",
        contamination="NONE",
        ai_confidence="HIGH",
        category=WasteCategory.RECYCLABLE.value,
        recommendation_confidence="HIGH",
        warning_count=0,
        processing_time_ms=100,
        status="SUCCESS",
    )
    repo.create(old_record)
    repo.create(new_record)

    deleted_count = repo.delete_older_than(days=90)
    assert deleted_count == 1
    assert repo.get_by_request_id("old-req-1") is None
    assert repo.get_by_request_id("new-req-1") is not None


# ------------------------------------------------------------------------------
# 18. Strict Privacy Check: No Image Binary / URLs in Database Schema
# ------------------------------------------------------------------------------
def test_db_models_strictly_exclude_image_data():
    """Validates that table schemas have no column for image blobs or image URLs."""
    cls_columns = [col.name.lower() for col in ClassificationRecord.__table__.columns]
    fb_columns = [col.name.lower() for col in Feedback.__table__.columns]

    prohibited_terms = ["image", "photo", "picture", "file_data", "binary", "blob", "url"]
    for col in cls_columns:
        for term in prohibited_terms:
            assert term not in col, f"Prohibited image/URL storage column found: {col}"
    for col in fb_columns:
        for term in prohibited_terms:
            assert term not in col, f"Prohibited image/URL storage column found: {col}"


# ------------------------------------------------------------------------------
# 19. Metrics Endpoint Protection with API Key
# ------------------------------------------------------------------------------
def test_metrics_endpoint_admin_api_key_protection(client: TestClient):
    """Test that configuring METRICS_API_KEY restricts access unless X-Admin-API-Key is provided."""
    from app.core.config import settings

    original_key = settings.METRICS_API_KEY
    settings.METRICS_API_KEY = "super-secret-admin-key"

    try:
        # Request without header should be rejected with 403
        unauth_res = client.get("/api/v1/metrics")
        assert unauth_res.status_code == 403
        assert unauth_res.json()["error"]["code"] == "FORBIDDEN"

        # Request with wrong header should be rejected with 403
        bad_key_res = client.get("/api/v1/metrics", headers={"X-Admin-API-Key": "wrong-key"})
        assert bad_key_res.status_code == 403
        assert bad_key_res.json()["error"]["code"] == "FORBIDDEN"

        # Request with correct header should succeed with 200
        auth_res = client.get(
            "/api/v1/metrics",
            headers={"X-Admin-API-Key": "super-secret-admin-key"},
        )
        assert auth_res.status_code == 200
        assert "total_classifications" in auth_res.json()
    finally:
        settings.METRICS_API_KEY = original_key


# ------------------------------------------------------------------------------
# 20. Feedback Validation Boundaries and Status Codes
# ------------------------------------------------------------------------------
def test_feedback_rating_boundaries(client: TestClient):
    """Test that rating values outside 1-5 (e.g. 0, -1, 6) are rejected with 400."""
    res_zero = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "test-req-id",
            "rating": 0,
            "feedback_type": "HELPFUL",
        },
    )
    assert res_zero.status_code == 400
    assert res_zero.json()["error"]["code"] == "VALIDATION_ERROR"

    res_six = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "test-req-id",
            "rating": 6,
            "feedback_type": "HELPFUL",
        },
    )
    assert res_six.status_code == 400
    assert res_six.json()["error"]["code"] == "VALIDATION_ERROR"


def test_feedback_non_existent_request_id(client: TestClient):
    """Test that feedback for a non-existent classification request returns 404 RESOURCE_NOT_FOUND."""
    res = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "non-existent-uuid-99999",
            "rating": 5,
            "feedback_type": "HELPFUL",
        },
    )
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "not found" in data["error"]["message"].lower()


def test_feedback_duplicate_conflict(client: TestClient, db_session: Session):
    """Test that submitting duplicate feedback for the same request_id returns 409 RESOURCE_CONFLICT."""
    repo = ClassificationRepository(db_session)
    record = ClassificationRecord(
        request_id="conflict-req-123",
        input_type="TEXT",
        item_name="test item",
        material="plastic",
        condition="clean",
        contamination="NONE",
        ai_confidence="HIGH",
        category="RECYCLABLE",
        recommendation_confidence="HIGH",
        status="SUCCESS",
    )
    repo.create(record)

    # First submission -> 201 Created
    first_res = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "conflict-req-123",
            "rating": 4,
            "feedback_type": "HELPFUL",
        },
    )
    assert first_res.status_code == 201

    # Second submission -> 409 Conflict
    second_res = client.post(
        "/api/v1/feedback",
        json={
            "request_id": "conflict-req-123",
            "rating": 5,
            "feedback_type": "HELPFUL",
        },
    )
    assert second_res.status_code == 409
    data = second_res.json()
    assert data["error"]["code"] == "RESOURCE_CONFLICT"
    assert "already been submitted" in data["error"]["message"].lower()


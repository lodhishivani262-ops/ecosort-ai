"""EcoSort AI - Waste Classification & Recommendation Endpoint (Stage 5).

Unified and dedicated classification endpoints with integrated AI perception,
deterministic rule engine evaluation, and resilient database audit logging.
"""

import json
import logging
import time
from typing import Optional
from fastapi import APIRouter, Depends, File, Request, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile as StarletteUploadFile

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import ValidationException
from app.db.database import get_db
from app.rules.rule_engine import EcoSortRuleEngine
from app.schemas.classification import (
    ClassificationResultResponse,
    InputType,
    TextClassificationRequest,
    WastePerception,
    WasteRecommendation,
)
from app.schemas.common import ErrorResponse
from app.services.ai_service import BaseAIService, MockAIService, get_ai_service
from app.services.audit_service import AuditService
from app.utils.file_validation import validate_image_file

router = APIRouter()


def _log_audit_safely(
    db: Session,
    request_id: str,
    input_type: InputType,
    perception: WastePerception,
    recommendation: WasteRecommendation,
    processing_time_ms: int,
    session_id: Optional[str] = None,
) -> None:
    """Helper ensuring classification audit logging fails gracefully without impacting the user response."""
    try:
        audit_service = AuditService(db)
        audit_service.record_classification_resilient(
            request_id=request_id,
            input_type=input_type,
            perception=perception,
            recommendation=recommendation,
            processing_time_ms=processing_time_ms,
            session_id=session_id,
            status="SUCCESS",
        )
    except Exception as exc:
        logger.error(
            "Audit logging failed gracefully for request %s: %s",
            request_id,
            str(exc),
            exc_info=True,
        )


@router.post(
    "/classify",
    response_model=ClassificationResultResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error or invalid file type"},
        413: {"model": ErrorResponse, "description": "File exceeds maximum size limit (5MB)"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        502: {"model": ErrorResponse, "description": "Upstream AI provider or parsing error"},
        503: {"model": ErrorResponse, "description": "AI service unavailable or unconfigured"},
        504: {"model": ErrorResponse, "description": "AI provider timeout"},
    },
    summary="Classify and recommend waste disposal (Unified endpoint)",
    description=(
        "Full classification pipeline:\n"
        "1. Validates input format (multipart file or JSON text query)\n"
        "2. Executes AI Perception to observe item, material, condition, contamination\n"
        "3. Feeds structured perception into the deterministic EcoSort Rule Engine\n"
        "4. Resiliently logs structured audit metadata to persistent storage\n"
        "5. Returns structured perception alongside actionable disposal recommendations and safety guardrails."
    ),
)
@limiter.limit(settings.RATE_LIMIT)
async def classify_waste_unified(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    ai_service: BaseAIService = Depends(get_ai_service),
) -> ClassificationResultResponse:
    """Unified entry point for waste classification and disposal recommendation."""
    start_time = time.perf_counter()
    request_id = getattr(request.state, "request_id", "unknown-request-id")
    session_id = request.headers.get("x-session-id") or request.query_params.get("session_id")
    content_type = request.headers.get("content-type", "").lower()
    is_mock = isinstance(ai_service, MockAIService)

    # -------------------------------------------------------------------------
    # Case 1: JSON payload (Text classification)
    # -------------------------------------------------------------------------
    if "application/json" in content_type:
        try:
            body = await request.body()
            if not body or not body.strip():
                raise ValidationException("MISSING_INPUT", "Request body cannot be empty.")
            json_data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValidationException("INVALID_JSON", "Malformed or unparseable JSON payload.")

        if not isinstance(json_data, dict):
            raise ValidationException("INVALID_JSON", "JSON payload must be an object with a 'text' field.")

        try:
            req_model = TextClassificationRequest(**json_data)
        except ValidationError as val_err:
            first_err = val_err.errors()[0]
            msg = first_err.get("msg", "Invalid text input.")
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            raise ValidationException("VALIDATION_ERROR", msg)

        perception = await ai_service.analyze_text(req_model.text)
        recommendation = EcoSortRuleEngine.evaluate(perception)
        elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

        _log_audit_safely(
            db=db,
            request_id=request_id,
            input_type=InputType.TEXT,
            perception=perception,
            recommendation=recommendation,
            processing_time_ms=elapsed_ms,
            session_id=session_id,
        )

        return ClassificationResultResponse(
            request_id=request_id,
            input_type=InputType.TEXT,
            perception=perception,
            recommendation=recommendation,
            mock=is_mock,
        )

    # -------------------------------------------------------------------------
    # Case 2: Multipart form-data (Image upload or Form-based text)
    # -------------------------------------------------------------------------
    elif "multipart/form-data" in content_type:
        try:
            form = await request.form()
        except Exception:
            raise ValidationException("INVALID_FORM", "Malformed multipart form-data payload.")

        # Check for image file upload
        file_obj = form.get("file")
        if file_obj is not None and (
            isinstance(file_obj, (UploadFile, StarletteUploadFile)) or hasattr(file_obj, "read")
        ):
            content = await file_obj.read()
            filename = getattr(file_obj, "filename", None) or "upload.jpg"
            file_mime = getattr(file_obj, "content_type", None) or ""
            # Validate image in memory (magic bytes, size, MIME type, extension)
            detected_format, _ = validate_image_file(
                content=content,
                filename=filename,
                content_type=file_mime,
            )
            normalized_mime = "image/jpeg" if detected_format == "JPEG" else ("image/png" if detected_format == "PNG" else "image/webp")
            perception = await ai_service.analyze_image(
                image_bytes=content,
                filename=filename,
                mime_type=normalized_mime,
            )
            recommendation = EcoSortRuleEngine.evaluate(perception)
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

            _log_audit_safely(
                db=db,
                request_id=request_id,
                input_type=InputType.IMAGE,
                perception=perception,
                recommendation=recommendation,
                processing_time_ms=elapsed_ms,
                session_id=session_id,
            )

            return ClassificationResultResponse(
                request_id=request_id,
                input_type=InputType.IMAGE,
                perception=perception,
                recommendation=recommendation,
                mock=is_mock,
            )

        # Check for text field within form
        text_val = form.get("text")
        if text_val is not None:
            try:
                req_model = TextClassificationRequest(text=str(text_val))
            except ValidationError as val_err:
                first_err = val_err.errors()[0]
                msg = first_err.get("msg", "Invalid text input.")
                if msg.startswith("Value error, "):
                    msg = msg[len("Value error, "):]
                raise ValidationException("VALIDATION_ERROR", msg)

            perception = await ai_service.analyze_text(req_model.text)
            recommendation = EcoSortRuleEngine.evaluate(perception)
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

            _log_audit_safely(
                db=db,
                request_id=request_id,
                input_type=InputType.TEXT,
                perception=perception,
                recommendation=recommendation,
                processing_time_ms=elapsed_ms,
                session_id=session_id,
            )

            return ClassificationResultResponse(
                request_id=request_id,
                input_type=InputType.TEXT,
                perception=perception,
                recommendation=recommendation,
                mock=is_mock,
            )

        raise ValidationException(
            "MISSING_INPUT",
            "Must provide either an image 'file' or a 'text' query in the form data.",
        )

    # -------------------------------------------------------------------------
    # Case 3: Unsupported Content-Type or empty request
    # -------------------------------------------------------------------------
    else:
        raise ValidationException(
            "UNSUPPORTED_MEDIA_TYPE",
            "Content-Type must be 'application/json' or 'multipart/form-data'.",
            status_code=415,
        )


@router.post(
    "/classify/image",
    response_model=ClassificationResultResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
    summary="Classify waste item from image file",
    description="Dedicated image classification endpoint supporting native Swagger interactive file upload.",
)
@limiter.limit(settings.RATE_LIMIT)
async def classify_image_dedicated(
    request: Request,
    response: Response,
    file: UploadFile = File(..., description="Image file (JPEG, PNG, WEBP, max 5MB)"),
    db: Session = Depends(get_db),
    ai_service: BaseAIService = Depends(get_ai_service),
) -> ClassificationResultResponse:
    """Classifies an uploaded image file and returns disposal guidance."""
    start_time = time.perf_counter()
    request_id = getattr(request.state, "request_id", "unknown-request-id")
    session_id = request.headers.get("x-session-id") or request.query_params.get("session_id")
    content = await file.read()
    detected_format, _ = validate_image_file(
        content=content,
        filename=file.filename or "unknown.jpg",
        content_type=file.content_type or "",
    )
    normalized_mime = "image/jpeg" if detected_format == "JPEG" else ("image/png" if detected_format == "PNG" else "image/webp")
    perception = await ai_service.analyze_image(
        image_bytes=content,
        filename=file.filename or "upload.jpg",
        mime_type=normalized_mime,
    )
    recommendation = EcoSortRuleEngine.evaluate(perception)
    elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

    _log_audit_safely(
        db=db,
        request_id=request_id,
        input_type=InputType.IMAGE,
        perception=perception,
        recommendation=recommendation,
        processing_time_ms=elapsed_ms,
        session_id=session_id,
    )

    return ClassificationResultResponse(
        request_id=request_id,
        input_type=InputType.IMAGE,
        perception=perception,
        recommendation=recommendation,
        mock=isinstance(ai_service, MockAIService),
    )


@router.post(
    "/classify/text",
    response_model=ClassificationResultResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
    summary="Classify waste item from text query",
    description="Dedicated text classification endpoint supporting JSON request schema.",
)
@limiter.limit(settings.RATE_LIMIT)
async def classify_text_dedicated(
    request: Request,
    response: Response,
    payload: TextClassificationRequest,
    db: Session = Depends(get_db),
    ai_service: BaseAIService = Depends(get_ai_service),
) -> ClassificationResultResponse:
    """Classifies an item from text description and returns disposal guidance."""
    start_time = time.perf_counter()
    request_id = getattr(request.state, "request_id", "unknown-request-id")
    session_id = request.headers.get("x-session-id") or request.query_params.get("session_id")
    perception = await ai_service.analyze_text(payload.text)
    recommendation = EcoSortRuleEngine.evaluate(perception)
    elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

    _log_audit_safely(
        db=db,
        request_id=request_id,
        input_type=InputType.TEXT,
        perception=perception,
        recommendation=recommendation,
        processing_time_ms=elapsed_ms,
        session_id=session_id,
    )

    return ClassificationResultResponse(
        request_id=request_id,
        input_type=InputType.TEXT,
        perception=perception,
        recommendation=recommendation,
        mock=isinstance(ai_service, MockAIService),
    )

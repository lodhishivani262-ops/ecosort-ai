"""Tests for File and Image Security Validation Utilities."""

import pytest
from app.core.security import FileValidationException
from app.utils.file_validation import (
    detect_image_type_from_bytes,
    validate_image_file,
)


def test_detect_image_type_valid(valid_jpeg: bytes, valid_png: bytes, valid_webp: bytes):
    """Verify correct detection of authentic image format magic bytes."""
    assert detect_image_type_from_bytes(valid_jpeg) == "JPEG"
    assert detect_image_type_from_bytes(valid_png) == "PNG"
    assert detect_image_type_from_bytes(valid_webp) == "WEBP"


def test_detect_image_type_disguised_exe(disguised_exe: bytes):
    """Verify that executable files starting with MZ are rejected despite any extension."""
    with pytest.raises(FileValidationException) as exc_info:
        detect_image_type_from_bytes(disguised_exe)
    assert exc_info.value.code == "INVALID_FILE_TYPE"
    assert exc_info.value.status_code == 400


def test_validate_image_empty_file():
    """Verify that 0-byte uploads are rejected with EMPTY_FILE."""
    with pytest.raises(FileValidationException) as exc_info:
        validate_image_file(content=b"", filename="empty.jpg", content_type="image/jpeg")
    assert exc_info.value.code == "EMPTY_FILE"
    assert exc_info.value.status_code == 400


def test_validate_image_oversized(oversized_image: bytes):
    """Verify that images exceeding MAX_UPLOAD_SIZE_MB are rejected with 413 FILE_TOO_LARGE."""
    with pytest.raises(FileValidationException) as exc_info:
        validate_image_file(
            content=oversized_image,
            filename="large.jpg",
            content_type="image/jpeg",
        )
    assert exc_info.value.code == "FILE_TOO_LARGE"
    assert exc_info.value.status_code == 413


def test_validate_image_unsupported_mime(valid_jpeg: bytes):
    """Verify that non-image MIME types are rejected with 415 UNSUPPORTED_MEDIA_TYPE."""
    with pytest.raises(FileValidationException) as exc_info:
        validate_image_file(
            content=valid_jpeg,
            filename="test.jpg",
            content_type="text/plain",
        )
    assert exc_info.value.code == "UNSUPPORTED_MEDIA_TYPE"
    assert exc_info.value.status_code == 415


def test_validate_image_invalid_extension(valid_jpeg: bytes):
    """Verify that unsupported extensions are rejected."""
    with pytest.raises(FileValidationException) as exc_info:
        validate_image_file(
            content=valid_jpeg,
            filename="test.pdf",
            content_type="image/jpeg",
        )
    assert exc_info.value.code == "INVALID_FILE_TYPE"
    assert exc_info.value.status_code == 400


def test_validate_image_disguised_exe_file(disguised_exe: bytes):
    """Verify that an executable file renamed to .png is caught by magic bytes inspection."""
    with pytest.raises(FileValidationException) as exc_info:
        validate_image_file(
            content=disguised_exe,
            filename="disguised_malware.png",
            content_type="image/png",
        )
    assert exc_info.value.code == "INVALID_FILE_TYPE"
    assert exc_info.value.status_code == 400

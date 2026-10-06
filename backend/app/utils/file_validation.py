"""EcoSort AI - Secure Image and File Validation Utilities."""

from typing import Tuple
from app.core.config import settings
from app.core.security import FileValidationException

# Magic byte signatures for authorized web image formats
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
WEBP_RIFF_MAGIC = b"RIFF"
WEBP_TYPE_MAGIC = b"WEBP"

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg": "JPEG",
    "image/jpg": "JPEG",
    "image/png": "PNG",
    "image/webp": "WEBP",
}


def detect_image_type_from_bytes(data: bytes) -> str:
    """Inspects the binary signature (magic bytes) to verify actual file format.

    Guarantees that files renamed with fake extensions (e.g., malware.exe -> photo.jpg)
    are rejected.

    Returns:
        Canonical format string ("JPEG", "PNG", "WEBP") if recognized.

    Raises:
        FileValidationException: If magic bytes do not match allowed image formats.
    """
    if len(data) < 12:
        raise FileValidationException(
            code="INVALID_FILE_TYPE",
            message="File is too small or truncated to be a valid image.",
            status_code=400,
        )

    # Check JPEG
    if data.startswith(JPEG_MAGIC):
        return "JPEG"

    # Check PNG
    if data.startswith(PNG_MAGIC):
        return "PNG"

    # Check WEBP (RIFF header + WEBP tag at offset 8)
    if data.startswith(WEBP_RIFF_MAGIC) and data[8:12] == WEBP_TYPE_MAGIC:
        return "WEBP"

    raise FileValidationException(
        code="INVALID_FILE_TYPE",
        message="Unsupported image format. Allowed formats: JPEG, PNG, WEBP.",
        status_code=400,
    )


def validate_image_file(
    content: bytes,
    filename: str,
    content_type: str,
) -> Tuple[str, int]:
    """Performs full validation on an uploaded image file completely in memory.

    Validation steps:
    1. Check for empty payload (0 bytes).
    2. Check that file size does not exceed MAX_UPLOAD_SIZE_MB.
    3. Check declared MIME type against allowed image types.
    4. Check filename extension against allowed list.
    5. Perform deep binary signature inspection (magic bytes).

    Returns:
        Tuple of (detected_format, file_size_bytes)

    Raises:
        FileValidationException: On any validation failure with clean error code.
    """
    file_size = len(content)

    # 1. Reject empty files
    if file_size == 0:
        raise FileValidationException(
            code="EMPTY_FILE",
            message="Uploaded file is empty (0 bytes).",
            status_code=400,
        )

    # 2. Reject oversized files
    max_bytes = settings.max_upload_size_bytes
    if file_size > max_bytes:
        raise FileValidationException(
            code="FILE_TOO_LARGE",
            message=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB.",
            status_code=413,
        )

    # 3. Check declared Content-Type header
    normalized_mime = (content_type or "").lower().split(";")[0].strip()
    if normalized_mime not in ALLOWED_MIME_TYPES:
        raise FileValidationException(
            code="UNSUPPORTED_MEDIA_TYPE",
            message=f"Unsupported MIME type '{normalized_mime}'. Expected image/jpeg, image/png, or image/webp.",
            status_code=415,
        )

    # 4. Check filename extension
    lower_filename = (filename or "").lower()
    has_valid_extension = any(lower_filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)
    if not has_valid_extension:
        raise FileValidationException(
            code="INVALID_FILE_TYPE",
            message=f"Invalid file extension. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
            status_code=400,
        )

    # 5. Deep magic bytes verification (crucial defense against disguised executables)
    detected_format = detect_image_type_from_bytes(content)

    return detected_format, file_size

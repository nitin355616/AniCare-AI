import os
import uuid
from pathlib import Path
from typing import Tuple, Dict, Any
from fastapi import UploadFile, HTTPException, status
from app.config import settings

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp"
}

MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp"
}

def ensure_upload_dir() -> Path:
    """Ensures the upload directory exists and returns its Path object."""
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path

async def save_uploaded_image(file: UploadFile) -> Dict[str, Any]:
    """
    Validates uploaded file MIME type, size, and header bytes,
    then saves to uploads folder with a unique UUID filename.
    """
    # 1. Check Content-Type header
    content_type = file.content_type.lower() if file.content_type else ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{content_type}'. Allowed image formats are: JPEG, PNG, WEBP."
        )

    # 2. Read first chunk to check magic bytes and prevent execution of disguised binaries
    header = await file.read(16)
    if not header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    # Magic byte check
    is_valid_magic = False
    if header.startswith(b"\xff\xd8\xff"):
        is_valid_magic = True
    elif header.startswith(b"\x89PNG\r\n\x1a\n"):
        is_valid_magic = True
    elif header.startswith(b"RIFF") and b"WEBP" in header:
        is_valid_magic = True
    elif header.startswith(b"RIFF"):
        is_valid_magic = True

    if not is_valid_magic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content signature does not match a valid image. Executable or corrupted files are prohibited."
        )

    # 3. Read the rest and check maximum allowed size
    rest = await file.read()
    total_bytes = header + rest
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(total_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # 4. Generate safe unique filename
    image_id = f"IMG-{uuid.uuid4().hex[:12].upper()}"
    extension = ALLOWED_CONTENT_TYPES[content_type]
    safe_filename = f"{image_id}{extension}"

    upload_dir = ensure_upload_dir()
    destination = upload_dir / safe_filename

    # 5. Write to non-executable location safely
    with open(destination, "wb") as f:
        f.write(total_bytes)

    return {
        "image_id": image_id,
        "filename": safe_filename,
        "original_filename": file.filename or "unknown",
        "content_type": content_type,
        "file_size_bytes": len(total_bytes),
        "filepath": str(destination.resolve()),
        "url": f"/uploads/{safe_filename}"
    }

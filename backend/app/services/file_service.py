import os
import uuid
import base64
from typing import Tuple, Optional
from pathlib import Path
from ..utils.logging import logger

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_file(file_bytes: bytes, original_filename: str, custom_prefix: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Saves file bytes to disk with a secure filename.
    Returns: (document_id, stored_filename, full_file_path)
    """
    doc_id = custom_prefix or f"doc-{uuid.uuid4().hex[:8]}"
    _, ext = os.path.splitext(original_filename.lower())
    if not ext:
        ext = ".jpg"

    stored_filename = f"{doc_id}{ext}"
    file_path = UPLOAD_DIR / stored_filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    logger.info(f"Saved file {original_filename} as {stored_filename} ({len(file_bytes)} bytes)")
    return doc_id, stored_filename, str(file_path.resolve())

def save_base64_image(base64_str: str, filename_hint: str = "capture.jpg", custom_prefix: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Decodes a base64 image data string (e.g. from webcam capture) and saves it to disk.
    """
    if "," in base64_str:
        header, base64_data = base64_str.split(",", 1)
    else:
        base64_data = base64_str

    file_bytes = base64.b64decode(base64_data)
    return save_uploaded_file(file_bytes, filename_hint, custom_prefix=custom_prefix)

def get_file_path(stored_filename: str) -> Optional[str]:
    """Get absolute file path if file exists."""
    p = UPLOAD_DIR / stored_filename
    return str(p.resolve()) if p.exists() else None

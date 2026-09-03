from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from typing import Optional
from ...models.schemas import DocumentUploadResponse, LiveCaptureRequest
from ...utils.validation import validate_file_metadata, validate_image_content
from ...services.file_service import save_uploaded_file, save_base64_image
from ...storage.sqlite_store import sqlite_store as store
from ...utils.logging import logger

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Receives an uploaded document file (image, PDF, or DOCX)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    file_bytes = await file.read()
    file_size = len(file_bytes)

    is_valid, err_msg = validate_file_metadata(file.filename, file_size, file.content_type)
    if not is_valid:
        raise HTTPException(status_code=400, detail=err_msg)

    # Only validate image content for actual image files
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    dims = None
    if ext in ("jpg", "jpeg", "png"):
        is_valid_img, img_err, dims = validate_image_content(file_bytes)
        if not is_valid_img:
            raise HTTPException(status_code=400, detail=img_err)

    doc_id, stored_filename, full_path = save_uploaded_file(file_bytes, file.filename)

    store.save_document({
        "id": doc_id,
        "filename": file.filename,
        "stored_filename": stored_filename,
        "file_path": full_path,
        "file_size": file_size,
        "mime_type": file.content_type,
        "dimensions": dims,
        "status": "uploaded"
    })

    logger.info(f"Document registered: {doc_id} ({file.filename})")

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        uploaded_at=store.get_document(doc_id)["uploaded_at"],
        status="uploaded",
        message="Document uploaded successfully and ready for screening.",
        preview_url=f"/uploads/{stored_filename}"
    )

@router.post("/upload-live", response_model=DocumentUploadResponse)
async def upload_live_camera_capture(payload: LiveCaptureRequest):
    """
    Receives 2-step live camera snapshots:
    - document_base64: Auto-cropped ID card
    - face_base64: Live person selfie
    """
    doc_b64 = payload.document_base64 or payload.image_base64
    if not doc_b64:
        raise HTTPException(status_code=400, detail="Document image payload cannot be empty.")

    try:
        doc_id, stored_doc, doc_path = save_base64_image(
            doc_b64, 
            payload.filename or "cropped_document.jpg"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode document snapshot: {str(e)}")

    face_path = None
    stored_face = None
    if payload.face_base64:
        try:
            _, stored_face, face_path = save_base64_image(
                payload.face_base64,
                f"face_{doc_id}.jpg",
                custom_prefix=f"face_{doc_id}"
            )
            logger.info(f"Live face photo registered for document: {doc_id} -> {stored_face}")
        except Exception as e:
            logger.warning(f"Could not save live face snapshot: {e}")

    store.save_document({
        "id": doc_id,
        "filename": payload.filename or "live_document_scan.jpg",
        "stored_filename": stored_doc,
        "file_path": doc_path,
        "face_stored_filename": stored_face,
        "face_file_path": face_path,
        "capture_type": "2_step_live_kyc",
        "status": "uploaded"
    })

    logger.info(f"2-Step Live KYC registered: {doc_id} (Has Face Selfie: {bool(face_path)})")

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=payload.filename or "live_document_scan.jpg",
        uploaded_at=store.get_document(doc_id)["uploaded_at"],
        status="uploaded",
        message="Live document & face registered successfully.",
        preview_url=f"/uploads/{stored_doc}",
        face_preview_url=f"/uploads/{stored_face}" if stored_face else None
    )

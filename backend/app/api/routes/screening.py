from fastapi import APIRouter, HTTPException
import time
import os
from typing import Dict, Any
from ...models.schemas import (
    ScreeningResultResponse, ExtractedFields, FaceMatchResult,
    ValidationSummary, TamperingForensics, LedgerBlock
)
from ...services.image_service import (
    preprocess_image_for_model, perform_error_level_analysis, extract_exif_forensics
)
from ...services.ml_service import ml_service
from ...services.ocr_service import ocr_service
from ...services.face_service import face_service
from ...services.decision_service import decision_engine
from ...services.document_converter import convert_document_to_image
from ...utils.validation import validate_mrz_checksums, validate_document_dates, check_security_watchlist
from ...storage.sqlite_store import sqlite_store as store
from ...utils.logging import logger

router = APIRouter(prefix="/api/documents", tags=["screening"])

@router.post("/{document_id}/screen", response_model=ScreeningResultResponse)
async def screen_document(document_id: str):
    """
    Executes the comprehensive identity screening pipeline:
    1. Validates document existence
    2. Image preprocessing & quality analysis
    3. MobileNetV2 AI forgery classification
    4. OCR text extraction & ICAO Doc 9303 MRZ parsing (Module 1)
    5. ICAO 9303 checksums, date logic, and watchlist checks (Module 2)
    6. Error Level Analysis (ELA) and EXIF tampering forensics (Module 3)
    7. Biometric Face Cross-Matching (Module 4)
    8. Multi-signal decision & risk score calculation
    9. SHA-256 Cryptographic Hash Chained Audit Ledger (Blockchain theme)
    """
    start_time = time.time()
    doc = store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    file_path = doc.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="Document file path is unavailable.")

    try:
        # Step 1.5: Convert PDF/DOCX to image if needed & extract pure vector text
        image_path, was_converted, native_text = convert_document_to_image(file_path)
        if was_converted:
            logger.info(f"Document converted to image for screening: {image_path} (Has Native Text: {bool(native_text)})")

        # Step 2: Image Preprocessing (224x224 Lanczos, normalization, quality check)
        processed_batch, quality_meta = preprocess_image_for_model(image_path)

        # Step 3: Vision AI Prediction
        ml_result = ml_service.predict(processed_batch, image_path)

        # Step 4: Module 1 - OCR & MRZ Extraction (with Native Text Layer if present)
        ocr_result = ocr_service.extract_text(image_path, native_text=native_text)

        # Step 5: Module 2 - Document Validation Engine
        mrz_lines = ocr_result.get("mrz_lines") or []
        mrz_passed, mrz_details, mrz_inconsistencies = validate_mrz_checksums(mrz_lines)
        
        is_expired, expiry_status, date_inconsistencies = validate_document_dates(
            ocr_result.get("date_of_birth"),
            ocr_result.get("expiry_date")
        )
        
        watchlist_flagged, watchlist_details = check_security_watchlist(ocr_result.get("document_number"))

        all_inconsistencies = mrz_inconsistencies + date_inconsistencies
        validation_summary = {
            "mrz_checksum_passed": mrz_passed,
            "mrz_checksum_details": mrz_details,
            "is_expired": is_expired,
            "expiry_status": expiry_status,
            "watchlist_flagged": watchlist_flagged,
            "watchlist_details": watchlist_details,
            "logical_inconsistencies": all_inconsistencies
        }

        # Step 6: Module 3 - Forensic Tampering Analysis (ELA & EXIF)
        ela_data = perform_error_level_analysis(image_path)
        exif_data = extract_exif_forensics(image_path)

        tampering_forensics = {
            "ela_score": ela_data["ela_score"],
            "ela_status": ela_data["ela_status"],
            "metadata_flagged": exif_data["metadata_flagged"],
            "editing_software_detected": exif_data["editing_software_detected"],
            "anomaly_detected": bool(ela_data["anomaly_detected"] or exif_data["metadata_flagged"]),
            "tampering_details": exif_data["tampering_details"]
        }

        # Step 7: Module 4 - Biometric Face Verification
        face_path = doc.get("face_file_path")
        face_match = face_service.verify_faces(image_path, face_path)

        # Step 8: Multi-Signal Decision & Risk Engine Evaluation
        final_status, risk_level, risk_score, signals = decision_engine.evaluate(
            ml_result=ml_result,
            ocr_result=ocr_result,
            quality_metadata=quality_meta,
            tampering_forensics=tampering_forensics,
            validation_summary=validation_summary,
            face_match_result=face_match
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Ensure preview_url points to a browser-renderable image (e.g. for converted PDFs)
        if was_converted or image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            preview_url = f"/uploads/{os.path.basename(image_path)}"
        else:
            preview_url = f"/uploads/{doc.get('stored_filename')}" if doc.get("stored_filename") else None

        face_preview_url = f"/uploads/{doc.get('face_stored_filename')}" if doc.get("face_stored_filename") else None

        result_payload = {
            "document_id": document_id,
            "filename": doc.get("filename", "document.jpg"),
            "screening_status": final_status,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "genuine_probability": ml_result["genuine_probability"],
            "forged_probability": ml_result["forged_probability"],
            "model_confidence": ml_result["model_confidence"],
            "ocr_results": ocr_result,
            "validation_summary": validation_summary,
            "tampering_forensics": tampering_forensics,
            "face_match": face_match,
            "detected_signals": signals,
            "processing_time_ms": elapsed_ms,
            "preview_url": preview_url,
            "face_preview_url": face_preview_url
        }

        # Step 9: Save to store (attaches SHA-256 hash blockchain block)
        store.save_screening_result(document_id, result_payload)

        # Retrieve saved record with blockchain block attached
        saved_record = store.get_screening_result(document_id)
        ledger_block = saved_record.get("ledger_block", {})

        logger.info(f"Screening complete for {document_id}: {final_status} ({risk_level}, Score: {risk_score}) in {elapsed_ms}ms")

        return ScreeningResultResponse(
            document_id=document_id,
            filename=doc.get("filename", "document.jpg"),
            screening_status=final_status,
            risk_level=risk_level,
            risk_score=risk_score,
            genuine_probability=ml_result["genuine_probability"],
            forged_probability=ml_result["forged_probability"],
            model_confidence=ml_result["model_confidence"],
            ocr_results=ExtractedFields(
                name=ocr_result.get("name"),
                date_of_birth=ocr_result.get("date_of_birth"),
                document_number=ocr_result.get("document_number"),
                nationality=ocr_result.get("nationality"),
                expiry_date=ocr_result.get("expiry_date"),
                gender=ocr_result.get("gender"),
                document_type=ocr_result.get("document_type"),
                father_name=ocr_result.get("father_name"),
                visa_number=ocr_result.get("visa_number"),
                visa_type=ocr_result.get("visa_type"),
                stay_duration=ocr_result.get("stay_duration"),
                entry_validation=ocr_result.get("entry_validation"),
                mrz_lines=ocr_result.get("mrz_lines"),
                mrz_type=ocr_result.get("mrz_type"),
                raw_text=ocr_result.get("raw_text", ""),
                engine_used=ocr_result.get("engine_used"),
                is_clear=ocr_result.get("is_clear", True),
                clarity_message=ocr_result.get("clarity_message")
            ),
            validation_summary=ValidationSummary(
                mrz_checksum_passed=validation_summary["mrz_checksum_passed"],
                mrz_checksum_details=validation_summary["mrz_checksum_details"],
                is_expired=validation_summary["is_expired"],
                expiry_status=validation_summary["expiry_status"],
                watchlist_flagged=validation_summary["watchlist_flagged"],
                watchlist_details=validation_summary["watchlist_details"],
                logical_inconsistencies=validation_summary["logical_inconsistencies"]
            ),
            tampering_forensics=TamperingForensics(
                ela_score=tampering_forensics["ela_score"],
                ela_status=tampering_forensics["ela_status"],
                metadata_flagged=tampering_forensics["metadata_flagged"],
                editing_software_detected=tampering_forensics["editing_software_detected"],
                anomaly_detected=tampering_forensics["anomaly_detected"],
                tampering_details=tampering_forensics["tampering_details"]
            ),
            face_match=FaceMatchResult(
                face_verified=face_match.get("face_verified", False),
                match_score=face_match.get("match_score", 0.0),
                status=face_match.get("status", ""),
                details=face_match.get("details", "")
            ) if face_match else None,
            ledger_block=LedgerBlock(
                block_index=ledger_block.get("block_index", 1),
                block_hash=ledger_block.get("block_hash", ""),
                previous_hash=ledger_block.get("previous_hash", ""),
                timestamp=ledger_block.get("timestamp", ""),
                signature_algorithm=ledger_block.get("signature_algorithm", "SHA-256 Hash Chained Ledger"),
                integrity_status=ledger_block.get("integrity_status", "Verified Immutable Record")
            ) if ledger_block else None,
            detected_signals=signals,
            screening_timestamp=saved_record.get("screening_timestamp", ""),
            processing_time_ms=elapsed_ms,
            preview_url=preview_url,
            face_preview_url=face_preview_url
        )

    except Exception as e:
        logger.error(f"Error during screening of {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Screening pipeline error: {str(e)}")

@router.get("/{document_id}/result", response_model=ScreeningResultResponse)
async def get_screening_result(document_id: str):
    """Retrieves saved screening result for a document."""
    res = store.get_screening_result(document_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"No screening result found for document '{document_id}'.")

    ocr_data = res.get("ocr_results", {})
    val_data = res.get("validation_summary", {})
    tamper_data = res.get("tampering_forensics", {})
    face_data = res.get("face_match", {})
    block_data = res.get("ledger_block", {})

    return ScreeningResultResponse(
        document_id=res["document_id"],
        filename=res["filename"],
        screening_status=res["screening_status"],
        risk_level=res["risk_level"],
        risk_score=res.get("risk_score", 15),
        genuine_probability=res["genuine_probability"],
        forged_probability=res["forged_probability"],
        model_confidence=res["model_confidence"],
        ocr_results=ExtractedFields(
            name=ocr_data.get("name"),
            date_of_birth=ocr_data.get("date_of_birth"),
            document_number=ocr_data.get("document_number"),
            nationality=ocr_data.get("nationality"),
            expiry_date=ocr_data.get("expiry_date"),
            gender=ocr_data.get("gender"),
            document_type=ocr_data.get("document_type"),
            father_name=ocr_data.get("father_name"),
            visa_number=ocr_data.get("visa_number"),
            visa_type=ocr_data.get("visa_type"),
            stay_duration=ocr_data.get("stay_duration"),
            entry_validation=ocr_data.get("entry_validation"),
            mrz_lines=ocr_data.get("mrz_lines"),
            mrz_type=ocr_data.get("mrz_type"),
            raw_text=ocr_data.get("raw_text", ""),
            engine_used=ocr_data.get("engine_used"),
            is_clear=ocr_data.get("is_clear", True),
            clarity_message=ocr_data.get("clarity_message")
        ),
        validation_summary=ValidationSummary(
            mrz_checksum_passed=val_data.get("mrz_checksum_passed", True),
            mrz_checksum_details=val_data.get("mrz_checksum_details", "Standard verification"),
            is_expired=val_data.get("is_expired", False),
            expiry_status=val_data.get("expiry_status", "Valid"),
            watchlist_flagged=val_data.get("watchlist_flagged", False),
            watchlist_details=val_data.get("watchlist_details", ""),
            logical_inconsistencies=val_data.get("logical_inconsistencies", [])
        ),
        tampering_forensics=TamperingForensics(
            ela_score=tamper_data.get("ela_score", 0.0),
            ela_status=tamper_data.get("ela_status", "Normal"),
            metadata_flagged=tamper_data.get("metadata_flagged", False),
            editing_software_detected=tamper_data.get("editing_software_detected"),
            anomaly_detected=tamper_data.get("anomaly_detected", False),
            tampering_details=tamper_data.get("tampering_details", [])
        ),
        face_match=FaceMatchResult(
            face_verified=face_data.get("face_verified", False),
            match_score=face_data.get("match_score", 0.0),
            status=face_data.get("status", ""),
            details=face_data.get("details", "")
        ) if face_data else None,
        ledger_block=LedgerBlock(
            block_index=block_data.get("block_index", 1),
            block_hash=block_data.get("block_hash", ""),
            previous_hash=block_data.get("previous_hash", ""),
            timestamp=block_data.get("timestamp", ""),
            signature_algorithm=block_data.get("signature_algorithm", "SHA-256 Hash Chained Ledger"),
            integrity_status=block_data.get("integrity_status", "Verified Immutable Record")
        ) if block_data else None,
        detected_signals=res.get("detected_signals", []),
        screening_timestamp=res.get("screening_timestamp", ""),
        processing_time_ms=res.get("processing_time_ms"),
        preview_url=res.get("preview_url"),
        face_preview_url=res.get("face_preview_url")
    )

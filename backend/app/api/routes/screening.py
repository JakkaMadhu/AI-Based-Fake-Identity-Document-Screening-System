from fastapi import APIRouter, HTTPException
import time
import os
from typing import Dict, Any
from ...models.schemas import (
    ScreeningResultResponse, ExtractedFields, FaceMatchResult,
    ValidationSummary, TamperingForensics, LedgerBlock, RiskBreakdown
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


def _build_screening_response(res: Dict[str, Any]) -> ScreeningResultResponse:
    """Helper to transform a stored screening result record into ScreeningResultResponse."""
    ocr_data = res.get("ocr_results", {})
    val_data = res.get("validation_summary", {})
    tamper_data = res.get("tampering_forensics", {})
    face_data = res.get("face_match", {})
    block_data = res.get("ledger_block", {})

    return ScreeningResultResponse(
        document_id=res["document_id"],
        filename=res.get("filename", "document.jpg"),
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
            mother_name=ocr_data.get("mother_name"),
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
            ela_status=tamper_data.get("ela_status", "Normal compression profile"),
            metadata_flagged=tamper_data.get("metadata_flagged", False),
            editing_software_detected=tamper_data.get("editing_software_detected"),
            anomaly_detected=tamper_data.get("anomaly_detected", False),
            tampering_details=tamper_data.get("tampering_details", []),
            trufor_score=tamper_data.get("trufor_score"),
            is_tampered=tamper_data.get("is_tampered"),
            tamper_heatmap_url=tamper_data.get("tamper_heatmap_url"),
            tamper_overlay_url=tamper_data.get("tamper_overlay_url")
        ),
        face_match=FaceMatchResult(
            face_verified=face_data.get("face_verified", False),
            match_score=face_data.get("match_score", 0.0),
            status=face_data.get("status", ""),
            details=face_data.get("details", ""),
            is_face_clear=face_data.get("is_face_clear", True),
            clarity_issue=face_data.get("clarity_issue"),
            error_code=face_data.get("error_code")
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
        face_preview_url=res.get("face_preview_url"),
        tamper_heatmap_url=res.get("tamper_heatmap_url"),
        tamper_overlay_url=res.get("tamper_overlay_url"),
        risk_breakdown=RiskBreakdown(
            face_risk=res.get("risk_breakdown", {}).get("face_risk", 0.0),
            forgery_risk=res.get("risk_breakdown", {}).get("forgery_risk", 0.0),
            ocr_risk=res.get("risk_breakdown", {}).get("ocr_risk", 0.0),
            image_risk=res.get("risk_breakdown", {}).get("image_risk", 0.0),
            rule_risk=res.get("risk_breakdown", {}).get("rule_risk", 0.0),
            weighted_score=res.get("risk_breakdown", {}).get("weighted_score", 0.0),
            overrides_triggered=res.get("risk_breakdown", {}).get("overrides_triggered", [])
        ) if res.get("risk_breakdown") else None
    )


@router.post("/{document_id}/screen", response_model=ScreeningResultResponse)
async def screen_document(document_id: str):
    """
    Executes the comprehensive identity screening pipeline:
    1. Validates document existence
    2. Image preprocessing & quality analysis
    3. Vision AI forgery classification
    4. Sovereign Vision AI OCR & Entity Extraction (Qwen2.5-VL via Ollama)
    5. ICAO 9303 checksums, date logic, and watchlist checks
    6. Error Level Analysis (ELA) and EXIF tampering forensics
    7. Biometric Face Cross-Matching
    8. Multi-signal decision & risk score calculation
    9. SHA-256 Cryptographic Hash Chained Audit Ledger
    """
    start_time = time.time()
    doc = store.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{document_id}' not found.")

    file_path = doc.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="Document file path is unavailable.")

    try:
        # Step 1: Convert PDF/DOCX to 300 DPI high-res image if needed
        image_path, was_converted = convert_document_to_image(file_path)
        if was_converted:
            logger.info(f"Document converted to 300 DPI image for vision inspection: {image_path}")

        # Step 2: Image Preprocessing (quality analysis & normalization)
        processed_batch, quality_meta = preprocess_image_for_model(image_path)

        # Blank / Empty document immediate rejection fast-path
        if quality_meta.get("is_blank"):
            logger.warning(f"Screening aborted: Document {document_id} is completely blank or empty.")
            final_status = "Invalid Document"
            risk_level = "High Risk"
            risk_score = 100
            signals = [
                "Critical Validation Failure: Uploaded document is completely blank or empty. No optical features, text, or portrait present.",
                "Recommendation: IMMEDIATE REJECTION - Traveler must submit a valid physical identity document."
            ]
            elapsed_ms = int((time.time() - start_time) * 1000)
            preview_url = f"/uploads/{os.path.basename(image_path)}"
            face_preview_url = f"/uploads/{doc.get('face_stored_filename')}" if doc.get("face_stored_filename") else None

            result_payload = {
                "document_id": document_id,
                "filename": doc.get("filename", "document.jpg"),
                "screening_status": final_status,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "genuine_probability": 0.0,
                "forged_probability": 1.0,
                "model_confidence": 1.0,
                "ocr_results": {
                    "is_clear": False,
                    "clarity_message": "Document is completely blank or empty. No text could be detected.",
                    "raw_text": ""
                },
                "validation_summary": {
                    "mrz_checksum_passed": False,
                    "mrz_checksum_details": "No MRZ lines present (blank document)",
                    "is_expired": False,
                    "expiry_status": "Document Invalid",
                    "watchlist_flagged": False,
                    "watchlist_details": "N/A",
                    "logical_inconsistencies": ["Empty / blank document file provided"]
                },
                "tampering_forensics": {
                    "ela_score": 0.0,
                    "ela_status": "Uniform empty frame",
                    "metadata_flagged": False,
                    "anomaly_detected": True,
                    "tampering_details": ["Image lacks optical entropy and feature gradients"],
                    "trufor_score": 0.0,
                    "is_tampered": True
                },
                "face_match": None,
                "detected_signals": signals,
                "processing_time_ms": elapsed_ms,
                "preview_url": preview_url,
                "face_preview_url": face_preview_url,
                "risk_breakdown": {
                    "face_risk": 100.0,
                    "forgery_risk": 100.0,
                    "ocr_risk": 100.0,
                    "image_risk": 100.0,
                    "rule_risk": 100.0,
                    "weighted_score": 100.0,
                    "overrides_triggered": ["BLANK_DOCUMENT_REJECTION"]
                }
            }
            store.save_screening_result(document_id, result_payload)
            saved_record = store.get_screening_result(document_id)
            return _build_screening_response(saved_record)

        # Step 3: TruFor Vision AI Prediction (Forgery & Tampering Detection)
        ml_result = ml_service.predict(file_path=image_path, document_id=document_id, processed_batch=processed_batch)

        # Step 4: Module 1 - Sovereign Multimodal Vision OCR (Qwen2.5-VL via Ollama)
        ocr_result = ocr_service.extract_text(image_path)

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

        # Step 6: Module 3 - Forensic Tampering Analysis (TruFor, ELA & EXIF)
        ela_data = perform_error_level_analysis(image_path)
        exif_data = extract_exif_forensics(image_path)

        tampering_forensics = {
            "ela_score": ela_data["ela_score"],
            "ela_status": ela_data["ela_status"],
            "metadata_flagged": exif_data["metadata_flagged"],
            "editing_software_detected": exif_data["editing_software_detected"],
            "anomaly_detected": bool(ela_data["anomaly_detected"] or exif_data["metadata_flagged"] or ml_result.get("is_tampered")),
            "tampering_details": exif_data["tampering_details"],
            "trufor_score": ml_result.get("trufor_score", ml_result.get("forged_probability")),
            "is_tampered": ml_result.get("is_tampered", False),
            "tamper_heatmap_url": ml_result.get("tamper_heatmap_url"),
            "tamper_overlay_url": ml_result.get("tamper_overlay_url")
        }

        # Step 7: Module 4 - Biometric Face Verification
        face_path = doc.get("face_file_path")
        face_match = face_service.verify_faces(image_path, face_path)

        # Step 8: Multi-Signal Decision & Risk Engine Evaluation
        final_status, risk_level, risk_score, signals, risk_breakdown = decision_engine.evaluate(
            ml_result=ml_result,
            ocr_result=ocr_result,
            quality_metadata=quality_meta,
            tampering_forensics=tampering_forensics,
            validation_summary=validation_summary,
            face_match_result=face_match
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        # Preview URL
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
            "face_preview_url": face_preview_url,
            "tamper_heatmap_url": ml_result.get("tamper_heatmap_url"),
            "tamper_overlay_url": ml_result.get("tamper_overlay_url"),
            "risk_breakdown": risk_breakdown
        }

        # Step 9: Save to store (generates SHA-256 hash blockchain block)
        store.save_screening_result(document_id, result_payload)

        # Retrieve saved record with blockchain block attached
        saved_record = store.get_screening_result(document_id)

        logger.info(f"Screening complete for {document_id}: {final_status} ({risk_level}, Score: {risk_score}) in {elapsed_ms}ms")
        return _build_screening_response(saved_record)

    except Exception as e:
        logger.error(f"Error during screening of {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Screening pipeline error: {str(e)}")


@router.get("/{document_id}/result", response_model=ScreeningResultResponse)
async def get_screening_result(document_id: str):
    """Retrieves saved screening result for a document."""
    res = store.get_screening_result(document_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"No screening result found for document '{document_id}'.")

    return _build_screening_response(res)

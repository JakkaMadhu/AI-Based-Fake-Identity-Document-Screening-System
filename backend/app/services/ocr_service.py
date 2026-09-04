"""
Module 1: Unified Vision AI Document OCR & Parameter Extraction Service.
Delegates document visual reading and entity comprehension directly to
local sovereign Vision-Language Models (Qwen2.5-VL 7B) via Ollama.
"""

import os
from typing import Dict, Any, Optional
from ..utils.logging import logger
from .ollama_service import ollama_service


class OCRService:
    """
    Unified AI Document OCR & Parameter Extraction.
    Uses sovereign multimodal vision intelligence to simultaneously read text,
    understand document structure, and extract structured identity attributes.
    """

    def __init__(self):
        self._qr_detector = None
        self._init_qr_detector()

    def _init_qr_detector(self):
        """Optional hardware/OpenCV QR detector for digital ID barcode cross-verification."""
        try:
            import cv2
            self._cv2 = cv2
            self._qr_detector = cv2.QRCodeDetector()
            logger.info("OpenCV QR code detector initialized.")
        except Exception:
            self._qr_detector = None

    def _decode_qr_if_present(self, image_path: str) -> Dict[str, Any]:
        """Directly decodes secure QR codes if embedded on identity cards."""
        qr_fields: Dict[str, Any] = {}
        if not self._qr_detector:
            return qr_fields

        try:
            img = self._cv2.imread(image_path)
            if img is not None:
                data, _, _ = self._qr_detector.detectAndDecode(img)
                if data:
                    logger.info(f"Identity QR code detected and decoded: {data[:50]}...")
                    # Basic extraction for UIDAI / travel secure QR payloads
                    import re
                    name_m = re.search(r'name="([^"]+)"', data, re.IGNORECASE) or re.search(r'name:([^\n,]+)', data, re.IGNORECASE)
                    if name_m:
                        qr_fields["name"] = name_m.group(1).strip()

                    dob_m = re.search(r'dob="([^"]+)"', data, re.IGNORECASE) or re.search(r'dob:([^\n,]+)', data, re.IGNORECASE)
                    if dob_m:
                        qr_fields["date_of_birth"] = dob_m.group(1).strip()

                    uid_m = re.search(r'uid="([0-9]{12})"', data)
                    if uid_m:
                        raw_u = uid_m.group(1)
                        qr_fields["document_number"] = f"{raw_u[:4]} {raw_u[4:8]} {raw_u[8:]}"
        except Exception as e:
            logger.debug(f"QR pass skipped: {e}")

        return qr_fields

    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Executes end-to-end multimodal vision extraction via Ollama Qwen2.5-VL.
        """
        raw_text = ""
        engine_used = "Ollama Vision (qwen2.5vl:7b)"
        is_clear = True
        clarity_message = "Document text successfully extracted via Vision AI."

        fields: Dict[str, Any] = {}

        try:
            fields = ollama_service.extract_from_image(image_path)
            raw_text = fields.get("raw_text") or ""
            engine_used = fields.get("engine_used") or engine_used

            if not raw_text.strip():
                is_clear = False
                clarity_message = "Document image is blurred, low-resolution, or unreadable. Please upload a clear document scan."

        except Exception as e:
            logger.error(f"Vision AI extraction error: {e}")
            is_clear = False
            engine_used = "Extraction Unavailable"
            clarity_message = f"AI Vision model error: {str(e)}. Ensure Ollama is running with qwen2.5vl:7b."
            fields = {
                "raw_text": "",
                "name": None,
                "document_number": None,
                "date_of_birth": None,
                "gender": None,
                "father_name": None,
                "mother_name": None,
                "nationality": None,
                "expiry_date": None,
                "document_type": None,
                "mrz_lines": None
            }

        # Cross-verify with authentic secure QR code if present on the document
        qr_data = self._decode_qr_if_present(image_path)
        for k, v in qr_data.items():
            if v and not fields.get(k):
                fields[k] = v

        return {
            "name": fields.get("name"),
            "date_of_birth": fields.get("date_of_birth"),
            "document_number": fields.get("document_number"),
            "nationality": fields.get("nationality") or "IND",
            "expiry_date": fields.get("expiry_date"),
            "gender": fields.get("gender"),
            "document_type": fields.get("document_type") or "Identity Document",
            "father_name": fields.get("father_name"),
            "mother_name": fields.get("mother_name"),
            "visa_number": fields.get("visa_number"),
            "visa_type": fields.get("visa_type"),
            "stay_duration": fields.get("stay_duration"),
            "entry_validation": fields.get("entry_validation"),
            "mrz_lines": fields.get("mrz_lines") or [],
            "mrz_type": fields.get("mrz_type"),
            "raw_text": raw_text.strip(),
            "engine_used": engine_used,
            "is_clear": is_clear,
            "clarity_message": clarity_message
        }


# Global singleton
ocr_service = OCRService()

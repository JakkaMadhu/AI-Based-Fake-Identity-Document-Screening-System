from typing import Dict, Any, List, Tuple, Optional
from ..utils.logging import logger

class DecisionEngine:
    """
    Transparent Decision & Risk Engine.
    Implements a 5-Factor Weighted Risk Algorithm (30/30/20/10/10) with Critical Hard Overrides:
      - 30% Biometric Face Mismatch (FaceRisk)
      - 30% SOTA TruFor Forgery Evidence (ForgeryRisk)
      - 20% OCR & Entity Extraction Consistency (OCRRisk)
      - 10% Optical Focus, Blur & Image Quality (ImageRisk)
      - 10% ICAO Doc 9303 Rules, MRZ & Expiry (RuleRisk)
    
    Hard Overrides prevent signal dilution by immediately escalating fatal smoking guns
    (e.g., photoshopped image, imposter traveler, or counterfeit check digits) to FAKE.
    """

    def evaluate(
        self,
        ml_result: Dict[str, Any],
        ocr_result: Dict[str, Any],
        quality_metadata: Dict[str, Any],
        tampering_forensics: Dict[str, Any],
        validation_summary: Dict[str, Any],
        face_match_result: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, int, List[str], Dict[str, Any]]:
        """
        Calculates:
        - final_status: "REAL (AUTHENTIC)" | "FAKE (FORGED / TAMPERED)" | "REQUIRES MANUAL REVIEW" | "INVALID DOCUMENT"
        - risk_level: "Low Risk" | "Medium Risk" | "High Risk"
        - risk_score: 0 - 100
        - detected_signals: List[str]
        - risk_breakdown: Dict with 5 weights and any triggered hard overrides
        """
        signals: List[str] = []
        overrides_triggered: List[str] = []

        # 0. Blank / Empty Document Critical Gate
        if quality_metadata.get("is_blank"):
            signals.append("Critical Validation Failure: Uploaded document is completely blank or empty. No optical features, text, or portrait present.")
            signals.append("Recommendation: IMMEDIATE REJECTION - Traveler must submit a valid physical identity document.")
            risk_breakdown = {
                "face_risk": 100.0,
                "forgery_risk": 100.0,
                "ocr_risk": 100.0,
                "image_risk": 100.0,
                "rule_risk": 100.0,
                "weighted_score": 100.0,
                "overrides_triggered": ["BLANK_DOCUMENT_REJECTION"]
            }
            return "INVALID DOCUMENT", "High Risk", 100, signals, risk_breakdown

        # ============================================================
        # FACTOR 1: BIOMETRIC FACE RISK (30% WEIGHT)
        # ============================================================
        face_risk = 0.0
        face_mismatch = False

        if face_match_result:
            err_code = face_match_result.get("error_code")
            status_text = face_match_result.get("status", "")
            match_score = face_match_result.get("match_score", 0.0)
            match_pct = match_score * 100
            is_face_clear = face_match_result.get("is_face_clear", True)
            clarity_issue = face_match_result.get("clarity_issue")

            if err_code == "NO_FACE_IN_LIVE" or "No Face Detected in Live" in status_text:
                face_risk = 100.0
                face_mismatch = True
                signals.append("Biometric Compliance Failure: No human face detected in the live camera capture. Traveler must present themselves in front of camera.")
            elif err_code == "NO_FACE_IN_DOC" or "No Face Detected in Document" in status_text:
                face_risk = 70.0
                signals.append("Biometric Warning: Document image does not contain an extractable portrait photo. Secondary physical verification required.")
            elif err_code == "FACE_NOT_CLEAR" or (not is_face_clear and not face_match_result.get("face_verified")):
                # FACE IS NOT CLEAR / MOTION BLUR / LOW RES -> INCONCLUSIVE (NOT AN IMPERSONATOR!)
                face_risk = 40.0
                face_mismatch = False  # Critical: Do NOT treat as criminal impersonation!
                signals.append(f"Biometric Quality Advisory: Face is not clear — {clarity_issue or 'Motion blur, low lighting, or poor resolution detected'}. Biometric match is inconclusive.")
                signals.append("Recommendation: RETAKE LIVE SELFIE - Traveler must hold still, keep hands away from face, and face the camera directly.")
            elif match_score > 0:
                face_risk = round(max(0.0, min(100.0, (1.0 - match_score) * 100.0)), 1)
                if face_match_result.get("face_verified"):
                    signals.append(f"Biometric Verification Confirmed: {match_pct:.1f}% facial similarity between live face and document portrait.")
                else:
                    face_mismatch = True
                    signals.append(f"Biometric Impersonation Alert: Live traveler does not match document portrait (Match Score: {match_pct:.1f}%).")

        # ============================================================
        # FACTOR 2: TRUFOR FORGERY & SPLICING RISK (30% WEIGHT)
        # ============================================================
        trufor_score = ml_result.get("trufor_score", ml_result.get("forged_probability", 0.0))
        is_tampered = ml_result.get("is_tampered", trufor_score >= 0.50)
        forgery_risk = round(trufor_score * 100.0, 1)

        ela_score = tampering_forensics.get("ela_score", 0.0)
        if tampering_forensics.get("anomaly_detected"):
            forgery_risk = max(forgery_risk, 75.0)
            signals.append(f"Forensic Tampering Alert: Error Level Analysis variance (score: {ela_score:.2f}) indicates digital photo or text modification.")
        elif ela_score > 0.40:
            signals.append("Localized JPEG compression variance detected along text boundaries.")

        if tampering_forensics.get("metadata_flagged"):
            forgery_risk = max(forgery_risk, 80.0)
            software = tampering_forensics.get("editing_software_detected") or "External graphics software"
            signals.append(f"Metadata Anomaly: File created or modified using prohibited editing suite ({software}).")

        if is_tampered or forgery_risk >= 65.0:
            signals.append(f"TruFor Neural Splicing Alert: High forensic anomaly score ({trufor_score:.4f}) indicates localized pixel tampering / forged text insertion.")
        else:
            signals.append(f"TruFor Forensics Confirmed: Document pixel grid and compression artifacts indicate authentic, unmanipulated structure (Score: {trufor_score:.4f}).")

        # ============================================================
        # FACTOR 3: OCR & ENTITY CONSISTENCY RISK (20% WEIGHT)
        # ============================================================
        ocr_risk = 0.0
        if not ocr_result.get("is_clear", True):
            ocr_risk += 50.0
            clarity_msg = ocr_result.get("clarity_message") or "Document is not clear, blurry, or low contrast. Unable to extract complete text."
            signals.append(f"Document Clarity Alert: {clarity_msg}")

        if not ocr_result.get("name"):
            ocr_risk += 15.0
        if not ocr_result.get("document_number"):
            ocr_risk += 15.0

        for inc in validation_summary.get("logical_inconsistencies", []):
            ocr_risk += 20.0
            signals.append(f"Validation Inconsistency: {inc}")

        ocr_risk = min(100.0, ocr_risk)

        # ============================================================
        # FACTOR 4: IMAGE QUALITY, BLUR & ILLUMINATION RISK (10% WEIGHT)
        # ============================================================
        image_risk = 0.0
        if quality_metadata.get("is_blurry"):
            sharpness = quality_metadata.get("sharpness_score", 0.0)
            image_risk += 65.0
            signals.append(f"Optical Blur Alert: Image edge sharpness ({sharpness:.1f}) is below standard forensic legibility threshold (35.0). Microprint, holograms, and fine text are degraded.")

        if quality_metadata.get("is_too_dark"):
            image_risk += 25.0
            signals.append("Image underexposed: Low ambient lighting may degrade feature detection.")
        elif quality_metadata.get("is_too_bright"):
            image_risk += 25.0
            signals.append("Image overexposed: Glare or specular reflection detected.")

        if quality_metadata.get("contrast_rms", 100) < 30:
            image_risk += 15.0
            signals.append("Low contrast image: Fine micro-print security patterns obscured.")

        image_risk = min(100.0, image_risk)

        # ============================================================
        # FACTOR 5: ICAO DOC 9303, MRZ & RULE RISK (10% WEIGHT)
        # ============================================================
        rule_risk = 0.0
        if not validation_summary.get("mrz_checksum_passed"):
            rule_risk += 80.0
            signals.append("ICAO Doc 9303 Compliance Failure: Check digit mismatch in Machine Readable Zone.")

        if validation_summary.get("is_expired"):
            rule_risk += 60.0
            signals.append(f"Document Status: {validation_summary.get('expiry_status')}")

        if validation_summary.get("watchlist_flagged"):
            rule_risk = 100.0
            signals.append(f"CRITICAL SECURITY ALERT: {validation_summary.get('watchlist_details')}")

        rule_risk = min(100.0, rule_risk)

        # ============================================================
        # WEIGHTED FORMULA (0.30 Face + 0.30 Forgery + 0.20 OCR + 0.10 Image + 0.10 Rule)
        # ============================================================
        weighted_score = round(
            (0.30 * face_risk) +
            (0.30 * forgery_risk) +
            (0.20 * ocr_risk) +
            (0.10 * image_risk) +
            (0.10 * rule_risk),
            1
        )

        # ============================================================
        # HARD OVERRIDES (PREVENTS SIGNAL DILUTION)
        # ============================================================
        if forgery_risk >= 70.0 or is_tampered:
            overrides_triggered.append("CRITICAL FORGERY: SOTA TruFor / ELA detected pixel-level splicing or manipulation")
        if face_risk >= 75.0 or face_mismatch:
            overrides_triggered.append("CRITICAL BIOMETRIC: Live traveler does not match document portrait (Impersonation)")
        if not validation_summary.get("mrz_checksum_passed"):
            overrides_triggered.append("CRITICAL CHECKSUM: ICAO Doc 9303 check digit calculation failed (Altered document numbers)")
        if validation_summary.get("watchlist_flagged"):
            overrides_triggered.append("CRITICAL WATCHLIST: Active lookout circular / security watchlist match")

        # ============================================================
        # FINAL STATUS & RISK DETERMINATION
        # ============================================================
        final_risk_score = int(weighted_score)

        if len(overrides_triggered) > 0 or final_risk_score >= 65:
            final_status = "FAKE (FORGED / TAMPERED)"
            risk_level = "High Risk"
            final_risk_score = max(final_risk_score, 75)
            signals.append("Recommendation: IMMEDIATE INTERVENTION - Refer traveler to secondary inspection counter.")
        elif (
            final_risk_score >= 30 
            or validation_summary.get("is_expired") 
            or quality_metadata.get("is_blurry") 
            or ml_result.get("model_confidence", 1.0) < 0.60
            or (face_match_result and not face_match_result.get("is_face_clear", True) and not face_match_result.get("face_verified"))
        ):
            final_status = "REQUIRES MANUAL REVIEW"
            risk_level = "Medium Risk"
            final_risk_score = max(final_risk_score, 35)
            signals.append("Recommendation: MANUAL REVIEW - Officer inspection of physical document or selfie retake required.")
        else:
            final_status = "REAL (AUTHENTIC)"
            risk_level = "Low Risk"
            signals.append("Recommendation: CLEAR TRAVELER - Document and biometric parameters verified.")

        final_risk_score = min(100, max(0, final_risk_score))

        risk_breakdown = {
            "face_risk": round(face_risk, 1),
            "forgery_risk": round(forgery_risk, 1),
            "ocr_risk": round(ocr_risk, 1),
            "image_risk": round(image_risk, 1),
            "rule_risk": round(rule_risk, 1),
            "weighted_score": round(weighted_score, 1),
            "overrides_triggered": overrides_triggered
        }

        return final_status, risk_level, final_risk_score, signals, risk_breakdown

decision_engine = DecisionEngine()

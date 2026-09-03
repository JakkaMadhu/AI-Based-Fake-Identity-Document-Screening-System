from typing import Dict, Any, List, Tuple, Optional
from ..utils.logging import logger

class DecisionEngine:
    """
    Transparent Decision & Risk Engine.
    Synthesizes vision AI probabilities, ELA tampering forensics, EXIF metadata,
    ICAO 9303 MRZ check digits, date validity, security watchlists, and facial biometrics.
    Computes a quantitative Risk Score (0 - 100).
    """
    def evaluate(
        self,
        ml_result: Dict[str, Any],
        ocr_result: Dict[str, Any],
        quality_metadata: Dict[str, Any],
        tampering_forensics: Dict[str, Any],
        validation_summary: Dict[str, Any],
        face_match_result: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, int, List[str]]:
        """
        Calculates:
        - final_status: "Likely Genuine" | "Suspicious" | "Requires Manual Review"
        - risk_level: "Low Risk" | "Medium Risk" | "High Risk"
        - risk_score: 0 - 100
        - detected_signals: List[str]
        """
        forged_prob = ml_result["forged_probability"]
        confidence = ml_result["model_confidence"]
        signals: List[str] = []

        risk_score = int(forged_prob * 45) # Base vision risk (0 - 45)

        # 0. Optical Clarity & Legibility Check
        if not ocr_result.get("is_clear", True):
            risk_score += 20
            clarity_msg = ocr_result.get("clarity_message") or "Document is not clear, blurry, or low contrast. Unable to extract complete text."
            signals.append(f"Document Clarity Alert: {clarity_msg}")

        # 1. Quality Analysis
        if quality_metadata.get("is_too_dark"):
            signals.append("Image underexposed: Low ambient lighting may degrade feature detection.")
            risk_score += 8
        elif quality_metadata.get("is_too_bright"):
            signals.append("Image overexposed: Glare or specular reflection detected.")
            risk_score += 8

        if quality_metadata.get("contrast_rms", 100) < 30:
            signals.append("Low contrast image: Fine micro-print security patterns obscured.")
            risk_score += 5

        # 2. Forensic Tampering Analysis (ELA & EXIF)
        ela_score = tampering_forensics.get("ela_score", 0.0)
        if tampering_forensics.get("anomaly_detected"):
            risk_score += 30
            signals.append(f"Forensic Tampering Alert: Error Level Analysis variance (score: {ela_score:.2f}) indicates digital photo or text modification.")
        elif ela_score > 0.40:
            risk_score += 15
            signals.append("Localized JPEG compression variance detected along text boundaries.")

        if tampering_forensics.get("metadata_flagged"):
            risk_score += 25
            software = tampering_forensics.get("editing_software_detected") or "External graphics software"
            signals.append(f"Metadata Anomaly: File created or modified using prohibited editing suite ({software}).")

        # 3. ICAO Doc 9303 Validation & Watchlist
        if not validation_summary.get("mrz_checksum_passed"):
            risk_score += 35
            signals.append("ICAO Doc 9303 Compliance Failure: Check digit mismatch in Machine Readable Zone.")
            for inc in validation_summary.get("logical_inconsistencies", []):
                signals.append(f"Validation Inconsistency: {inc}")

        if validation_summary.get("is_expired"):
            risk_score += 25
            signals.append(f"Document Status: {validation_summary.get('expiry_status')}")

        if validation_summary.get("watchlist_flagged"):
            risk_score += 50
            signals.append(f"CRITICAL SECURITY ALERT: {validation_summary.get('watchlist_details')}")

        # 4. Biometric Cross-Match
        face_mismatch = False
        if face_match_result and face_match_result.get("match_score", 0) > 0:
            match_pct = face_match_result["match_score"] * 100
            if face_match_result.get("face_verified"):
                signals.append(f"Biometric Verification Confirmed: {match_pct:.1f}% facial similarity between live face and document portrait.")
            else:
                face_mismatch = True
                risk_score += 45
                signals.append(f"Biometric Impersonation Alert: Live traveler does not match document portrait (Match Score: {match_pct:.1f}%).")

        # 5. Cap Risk Score
        risk_score = min(100, max(0, risk_score))

        # 6. Final Status Determination
        if risk_score >= 65 or face_mismatch or validation_summary.get("watchlist_flagged") or not validation_summary.get("mrz_checksum_passed"):
            final_status = "Suspicious"
            risk_level = "High Risk"
            signals.append("Recommendation: IMMEDIATE INTERVENTION - Refer traveler to secondary inspection counter.")
        elif risk_score >= 30 or validation_summary.get("is_expired") or confidence < 0.60:
            final_status = "Requires Manual Review"
            risk_level = "Medium Risk"
            signals.append("Recommendation: MANUAL REVIEW - Officer inspection of physical document required.")
        else:
            final_status = "Likely Genuine"
            risk_level = "Low Risk"
            signals.append("Recommendation: CLEAR TRAVELER - Document and biometric parameters verified.")

        return final_status, risk_level, risk_score, signals

decision_engine = DecisionEngine()

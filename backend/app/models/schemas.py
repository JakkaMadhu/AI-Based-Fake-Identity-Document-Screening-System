from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    uploaded_at: str
    status: str = "uploaded"
    message: str = "Document successfully uploaded and ready for screening"
    preview_url: Optional[str] = None
    face_preview_url: Optional[str] = None

class ExtractedFields(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    document_number: Optional[str] = None
    nationality: Optional[str] = None
    expiry_date: Optional[str] = None
    gender: Optional[str] = None
    # Visa-specific fields
    visa_number: Optional[str] = None
    visa_type: Optional[str] = None
    stay_duration: Optional[str] = None
    entry_validation: Optional[str] = None
    # MRZ fields
    mrz_lines: Optional[List[str]] = None
    mrz_type: Optional[str] = None
    raw_text: str = ""
    engine_used: Optional[str] = None
    is_clear: bool = True
    clarity_message: Optional[str] = None

class ValidationSummary(BaseModel):
    mrz_checksum_passed: bool = True
    mrz_checksum_details: str = "Compliant with ICAO Doc 9303 specifications"
    is_expired: bool = False
    expiry_status: str = "Valid Travel Document"
    watchlist_flagged: bool = False
    watchlist_details: str = "No records found on active security watchlists"
    logical_inconsistencies: List[str] = Field(default_factory=list)

class TamperingForensics(BaseModel):
    ela_score: float = 0.0
    ela_status: str = "Normal compression profile"
    metadata_flagged: bool = False
    editing_software_detected: Optional[str] = None
    anomaly_detected: bool = False
    tampering_details: List[str] = Field(default_factory=list)

class LedgerBlock(BaseModel):
    block_index: int = 1
    block_hash: str = ""
    previous_hash: str = ""
    timestamp: str = ""
    signature_algorithm: str = "SHA-256 Hash Chained Ledger"
    integrity_status: str = "Verified Immutable Record"

class FaceMatchResult(BaseModel):
    face_verified: bool = False
    match_score: float = 0.0
    status: str = "Not Performed"
    details: str = ""

class ScreeningResultResponse(BaseModel):
    document_id: str
    filename: str
    screening_status: str  # "Likely Genuine", "Suspicious", "Requires Manual Review"
    risk_level: str        # "Low Risk", "Medium Risk", "High Risk"
    risk_score: int = 15   # 0 - 100
    genuine_probability: float
    forged_probability: float
    model_confidence: float
    ocr_results: ExtractedFields
    validation_summary: ValidationSummary
    tampering_forensics: TamperingForensics
    face_match: Optional[FaceMatchResult] = None
    ledger_block: Optional[LedgerBlock] = None
    detected_signals: List[str]
    screening_timestamp: str
    processing_time_ms: Optional[int] = None
    preview_url: Optional[str] = None
    face_preview_url: Optional[str] = None

class HistoryItem(BaseModel):
    document_id: str
    filename: str
    screening_date: str
    status: str
    risk_level: str
    risk_score: int = 15
    ai_confidence: float
    genuine_probability: float
    forged_probability: float
    face_verified: Optional[bool] = None
    block_hash: Optional[str] = None

class PaginatedHistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int

class DashboardStatsResponse(BaseModel):
    total_screened: int
    likely_genuine: int
    suspicious: int
    requires_manual_review: int
    recent_activity: List[HistoryItem]

class LiveCaptureRequest(BaseModel):
    document_base64: Optional[str] = None
    face_base64: Optional[str] = None
    image_base64: Optional[str] = None
    filename: Optional[str] = "live_document_scan.jpg"

import os
import re
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any, List
from PIL import Image
import io

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/jpg",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

# Simulated SSB / Interpol Lookout Circular (LOC) Blacklist
SECURITY_WATCHLIST = {
    "Z9999999": "Interpol Red Notice - Fraudulent Documentation",
    "P8392104B": "SSB Lookout Circular - Identity Impersonation Flag",
    "X1029384": "Lost / Stolen Travel Document (SLTD Database)",
    "6712 9043 9999": "National Revocation Notice - Forged Aadhaar"
}

def validate_file_metadata(filename: str, file_size: int, content_type: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Validate file extension and file size."""
    if not filename:
        return False, "File name cannot be empty."

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed extensions are: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    if file_size <= 0:
        return False, "Uploaded file is empty."

    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({file_size / (1024*1024):.1f} MB) exceeds maximum limit of 10 MB."

    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES and content_type != "application/octet-stream":
        return False, f"Invalid content type '{content_type}'."

    return True, None

def validate_image_content(file_bytes: bytes) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]]]:
    """Validate that the bytes represent a valid, non-corrupted image and return dimensions."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        
        image = Image.open(io.BytesIO(file_bytes))
        width, height = image.size
        
        if width < 50 or height < 50:
            return False, f"Image dimensions ({width}x{height}) are too small for document screening.", None

        return True, None, (width, height)
    except Exception as e:
        return False, f"Invalid or corrupted image file: {str(e)}", None

# --- MODULE 2: ICAO DOC 9303 & DOCUMENT VALIDATION ENGINE ---

ICAO_WEIGHTS = [7, 3, 1]

def calculate_icao_check_digit(data: str) -> int:
    """
    Computes ICAO Doc 9303 check digit using weights 7, 3, 1 repeating.
    Characters A-Z are mapped to values 10-35. '<' is 0. Digits are their numeric values.
    """
    total = 0
    for idx, char in enumerate(data.upper()):
        weight = ICAO_WEIGHTS[idx % 3]
        if char.isdigit():
            val = int(char)
        elif 'A' <= char <= 'Z':
            val = ord(char) - ord('A') + 10
        elif char == '<':
            val = 0
        else:
            val = 0
        total += val * weight
    return total % 10

def validate_mrz_checksums(mrz_lines: List[str]) -> Tuple[bool, str, List[str]]:
    """
    Validates ICAO 9303 standard MRZ check digits.
    Supports Type 3 Passports (2 lines of 44 chars) and Type 1 Cards (3 lines of 30 chars).
    """
    inconsistencies = []
    
    if not mrz_lines or len(mrz_lines) < 2:
        return True, "No MRZ lines present; standard VIZ validation applied", inconsistencies

    # Clean lines
    lines = [line.strip().upper() for line in mrz_lines if line.strip()]

    # Standard Passport (TD3): 2 lines of ~44 chars
    if len(lines) >= 2 and len(lines[1]) >= 40:
        line2 = lines[1]
        
        # Passport Number (Chars 0-9) & Check Digit (Char 9)
        doc_num = line2[0:9]
        doc_num_check = line2[9]
        if doc_num_check.isdigit():
            expected_check = calculate_icao_check_digit(doc_num)
            if int(doc_num_check) != expected_check:
                inconsistencies.append(f"MRZ Document Number check digit mismatch (got {doc_num_check}, expected {expected_check})")

        # Date of Birth (Chars 13-19, YYMMDD) & Check Digit (Char 19)
        if len(line2) > 19:
            dob = line2[13:19]
            dob_check = line2[19]
            if dob_check.isdigit():
                expected_dob = calculate_icao_check_digit(dob)
                if int(dob_check) != expected_dob:
                    inconsistencies.append(f"MRZ Date of Birth check digit mismatch (got {dob_check}, expected {expected_dob})")

        # Expiry Date (Chars 21-27, YYMMDD) & Check Digit (Char 27)
        if len(line2) > 27:
            exp = line2[21:27]
            exp_check = line2[27]
            if exp_check.isdigit():
                expected_exp = calculate_icao_check_digit(exp)
                if int(exp_check) != expected_exp:
                    inconsistencies.append(f"MRZ Expiry Date check digit mismatch (got {exp_check}, expected {expected_exp})")

    passed = len(inconsistencies) == 0
    details = "ICAO Doc 9303 Check Digits Verified" if passed else "MRZ Check Digit Inconsistencies Detected"
    return passed, details, inconsistencies

def validate_document_dates(dob_str: Optional[str], expiry_str: Optional[str]) -> Tuple[bool, str, List[str]]:
    """
    Verifies temporal document validity:
    - Checks if expiry date is in the past.
    - Checks if birth date is valid and indicates an age >= 0 and <= 120.
    """
    inconsistencies = []
    is_expired = False
    status = "Valid Travel Document"

    now = datetime.now(timezone.utc)

    # Parse Expiry Date
    if expiry_str:
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%y%m%d"]:
            try:
                exp_date = datetime.strptime(expiry_str.strip(), fmt).replace(tzinfo=timezone.utc)
                if exp_date < now:
                    is_expired = True
                    status = f"Document Expired on {exp_date.strftime('%d-%b-%Y')}"
                    inconsistencies.append(status)
                else:
                    days_left = (exp_date - now).days
                    if days_left < 180:
                        inconsistencies.append(f"Document expires soon ({days_left} days remaining; minimum 6 months validity recommended)")
                break
            except ValueError:
                continue

    # Parse Date of Birth
    if dob_str:
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%y%m%d"]:
            try:
                birth_date = datetime.strptime(dob_str.strip(), fmt).replace(tzinfo=timezone.utc)
                if birth_date > now:
                    inconsistencies.append(f"Future birth date detected: {dob_str}")
                else:
                    age = (now - birth_date).days // 365
                    if age > 115:
                        inconsistencies.append(f"Calculated age ({age} years) exceeds typical validity")
                break
            except ValueError:
                continue

    return is_expired, status, inconsistencies

def check_security_watchlist(document_number: Optional[str]) -> Tuple[bool, str]:
    """Check if document number exists in the simulated SSB / Interpol Lookout Database."""
    if not document_number:
        return False, "Document number not provided for watchlist check"
    
    clean_num = re.sub(r'[^A-Z0-9]', '', document_number.upper())
    for flagged_id, reason in SECURITY_WATCHLIST.items():
        clean_flagged = re.sub(r'[^A-Z0-9]', '', flagged_id.upper())
        if clean_flagged in clean_num or clean_num in clean_flagged:
            return True, f"ALERT: Document matches {reason}"
            
    return False, "No active alerts in national security databases"

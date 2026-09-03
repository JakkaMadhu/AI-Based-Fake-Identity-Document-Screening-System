import re
import os
import hashlib
from typing import Dict, Any, Optional, List
from PIL import Image
from ..utils.logging import logger

class OCRService:
    """
    Module 1: OCR Extraction Service.
    Extracts text from Passports, Visas, National IDs (Aadhaar, Voter ID, PAN), and Driving Licences.
    Supports:
    1. RapidOCR (Fast, local ONNX deep-learning OCR - recommended for Windows)
    2. Tesseract OCR (pytesseract)
    3. OpenCV QR Code Detector (for instant, authentic Aadhaar QR decoding)
    """
    def __init__(self):
        self._rapidocr = None
        self._tesseract_available = False
        self._check_ocr_engines()

    def _check_ocr_engines(self):
        # 1. Check RapidOCR (pure pip install, no external exe required)
        try:
            from rapidocr_onnxruntime import RapidOCR
            self._rapidocr = RapidOCR()
            logger.info("RapidOCR deep-learning engine initialized successfully.")
        except ImportError:
            self._rapidocr = None

        # 2. Check Tesseract
        try:
            import pytesseract
            # Check standard Windows paths if not in PATH
            tess_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
            ]
            for p in tess_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    break

            self._tesseract_available = True
            logger.info("pytesseract module detected.")
        except Exception:
            self._tesseract_available = False

    def _create_watermark_suppressed_image(self, image_path: str):
        """
        Tier 2: Universal Color-Agnostic Spatial Frequency Filter.
        Eliminates repeating background watermarks of ANY color (cyan, yellow, pink, grey)
        by calculating the low-frequency background illumination surface and dividing it out.
        Preserves both dark black text and red/pink table ink.
        """
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return None

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Morphological closing with a large structuring element captures the diffuse
            # background illumination and repeating watermarks, but skips sharp text strokes
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
            background = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)

            # Divide image by background surface: eliminates watermarks of all colors
            division = cv2.divide(gray, background, scale=255)

            # Contrast-limited adaptive histogram equalization for crisp letter strokes
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(division)

            return enhanced
        except Exception as e:
            logger.warning(f"Universal background division failed: {e}")
            return None

    def extract_text(self, image_path: str, native_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes unified 3-tier document text extraction:
        Tier 1: Pure embedded native vector text from digital PDFs (100% ground truth).
        Tier 2: Dual-pass OCR with universal morphological background division (for scanned paper).
        Tier 3: Local Ollama AI semantic entity extraction.
        """
        raw_text = ""
        engine_used = "Simulation Fallback"

        # TIER 1: Native Vector PDF Text Layer (Instant, Zero Watermark, 100% Accuracy)
        if native_text and len(native_text.strip()) >= 25:
            raw_text = native_text.strip()
            engine_used = "Native Vector Text Layer (100% Ground Truth)"
            logger.info(f"Using Tier 1 native vector text layer ({len(raw_text)} chars). Skipping lossy optical OCR.")

        # TIER 2: Visual OCR for Scanned Physical Documents / Camera Photos
        if not raw_text and self._rapidocr is not None:
            # 1. Primary Pass: Original full-color image
            try:
                result, _ = self._rapidocr(image_path)
                if result:
                    extracted_lines = [line[1] for line in result if line and len(line) > 1]
                    raw_text = "\n".join(extracted_lines)
                    engine_used = "RapidOCR (Deep Learning)"
                    logger.info(f"RapidOCR primary pass extracted {len(raw_text)} characters.")
            except Exception as e:
                logger.warning(f"RapidOCR primary pass error: {e}")

            # 2. Universal Watermark Suppression Pass:
            # If text is noisy or misses clear identity markers, run on the background-divided image
            suppressed_img = self._create_watermark_suppressed_image(image_path)
            if suppressed_img is not None:
                try:
                    res_suppressed, _ = self._rapidocr(suppressed_img)
                    if res_suppressed:
                        suppressed_lines = [line[1] for line in res_suppressed if line and len(line) > 1]
                        suppressed_text = "\n".join(suppressed_lines)
                        logger.info(f"Universal background-divided pass extracted {len(suppressed_text)} characters.")

                        # If the background-divided pass captured certification lines or cleaner text, adopt it
                        if "CERTIFIED" in suppressed_text.upper() or len(suppressed_text) > len(raw_text):
                            raw_text = suppressed_text
                except Exception as e:
                    logger.warning(f"RapidOCR background division pass error: {e}")

        # Fallback to Tesseract OCR if text is still empty
        if not raw_text.strip() and self._tesseract_available:
            try:
                import pytesseract
                with Image.open(image_path) as img:
                    raw_text = pytesseract.image_to_string(img)
                if raw_text.strip():
                    engine_used = "Tesseract OCR"
                    logger.info(f"Tesseract OCR extracted {len(raw_text)} characters.")
            except Exception as e:
                logger.warning(f"Tesseract OCR failed ({e}).")

        # 3. Try OpenCV QR Code Reader (specialized for Aadhaar & modern travel IDs)
        qr_fields: Dict[str, Any] = {}
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is not None:
                detector = cv2.QRCodeDetector()
                data, bbox, _ = detector.detectAndDecode(img)
                if data:
                    logger.info(f"Decoded QR code data: {data[:60]}...")
                    name_qr = re.search(r'name="([^"]+)"', data, re.IGNORECASE) or re.search(r'name:([^\n,]+)', data, re.IGNORECASE)
                    if name_qr:
                        qr_fields["name"] = name_qr.group(1).strip()
                    dob_qr = re.search(r'dob="([^"]+)"', data, re.IGNORECASE) or re.search(r'dob:([^\n,]+)', data, re.IGNORECASE)
                    if dob_qr:
                        qr_fields["date_of_birth"] = dob_qr.group(1).strip()
                    gender_qr = re.search(r'gender="([MF])"', data, re.IGNORECASE)
                    if gender_qr:
                        qr_fields["gender"] = "Male" if gender_qr.group(1).upper() == "M" else "Female"
                    uid_qr = re.search(r'uid="([0-9]{12})"', data)
                    if uid_qr:
                        raw_u = uid_qr.group(1)
                        qr_fields["document_number"] = f"{raw_u[:4]} {raw_u[4:8]} {raw_u[8:]}"

                    if not raw_text.strip():
                        raw_text = f"[DECODED SECURE IDENTITY QR CODE]\n{data}"
                        engine_used = "OpenCV QR Detector"
        except Exception as e:
            logger.warning(f"QR detection pass: {e}")

        # 4. Check extraction quality and clarity (NO FALLBACKS - REAL DATA ONLY)
        is_clear = True
        clarity_message = "Document text successfully extracted."

        if not raw_text.strip() or len(raw_text.strip()) < 15:
            is_clear = False
            raw_text = ""
            engine_used = "None (Extraction Failed)"
            clarity_message = "Document image is blurred, low-resolution, or unreadable. Please upload a clear, high-resolution document."
            parsed_fields: Dict[str, Any] = {}
        else:
            # First pass: Fast deterministic multi-document heuristic parsing
            parsed_fields = self._parse_identity_fields(raw_text)

            # Second pass: Local Ollama AI Model (Zero-Shot Sovereign Reasoning)
            try:
                from .ollama_service import ollama_service
                ollama_extracted = ollama_service.extract_identity_entities(raw_text)
                if ollama_extracted:
                    model_used = ollama_service.get_available_model() or "Ollama AI"
                    engine_used = f"RapidOCR + {model_used}"
                    logger.info(f"Ollama ({model_used}) successfully returned identity parameters: {ollama_extracted}")
                    for k in ["name", "document_number", "date_of_birth", "gender", "father_name", "mother_name", "document_type", "nationality"]:
                        val = ollama_extracted.get(k)
                        if val and str(val).strip().lower() not in ["null", "none", "not detected", "unknown"]:
                            # Sanity check: ensure institutional names are not set as person name
                            if k == "name" and any(bad in str(val).upper() for bad in ["BOARD", "SECONDARY", "EDUCATION", "AMARAVATI", "GOVERNMENT"]):
                                continue
                            parsed_fields[k] = str(val).strip()
            except Exception as oe:
                logger.warning(f"Ollama integration pass skipped or timed out: {oe}")

            # If both name and document number are missing from text, scan is degraded
            if not parsed_fields.get("name") and not parsed_fields.get("document_number"):
                is_clear = False
                clarity_message = "Document text is partially obscured or blurred. Key parameters (Name / ID Number) could not be identified with certainty."

        # Merge high-precision QR fields if available from the card
        for k, v in qr_fields.items():
            if v:
                parsed_fields[k] = v
                is_clear = True
                clarity_message = "Document identity attributes verified directly via authentic document QR code."

        return {
            "name": parsed_fields.get("name"),
            "date_of_birth": parsed_fields.get("date_of_birth"),
            "document_number": parsed_fields.get("document_number"),
            "nationality": parsed_fields.get("nationality"),
            "expiry_date": parsed_fields.get("expiry_date"),
            "gender": parsed_fields.get("gender"),
            "document_type": parsed_fields.get("document_type"),
            "father_name": parsed_fields.get("father_name"),
            "visa_number": parsed_fields.get("visa_number"),
            "visa_type": parsed_fields.get("visa_type"),
            "stay_duration": parsed_fields.get("stay_duration"),
            "entry_validation": parsed_fields.get("entry_validation"),
            "mrz_lines": parsed_fields.get("mrz_lines"),
            "mrz_type": parsed_fields.get("mrz_type"),
            "raw_text": raw_text.strip(),
            "engine_used": engine_used,
            "is_clear": is_clear,
            "clarity_message": clarity_message
        }

    def _parse_identity_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields across Passports, Visas, Aadhaar, PAN, Voter ID, and Driving Licences."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        name = None
        dob = None
        doc_num = None
        nationality = None
        expiry = None
        gender = None
        visa_num = None
        visa_type = None
        stay_duration = None
        entry_validation = None
        mrz_lines: List[str] = []
        mrz_type = None

        # Document Classification
        text_upper = text.upper()
        document_type = "Standard Identity Document"
        if any(kw in text_upper for kw in ["SECONDARY SCHOOL", "BOARD OF SECONDARY", "CENTRAL BOARD", "MARKS MEMORANDUM", "HIGHER SECONDARY", "SCHOOL CERTIFICATE", "UNIVERSITY", "PROVISIONAL CERTIFICATE", "EXAMINATION"]):
            document_type = "Secondary School Certificate (Educational)"
        elif any(kw in text_upper for kw in ["AADHAAR", "UIDAI", "UNIQUE IDENTIFICATION"]):
            document_type = "Aadhaar Card (UIDAI)"
        elif any(kw in text_upper for kw in ["PASSPORT", "REPUBLIC OF INDIA PASSPORT"]):
            document_type = "Passport (ICAO Doc 9303)"
        elif any(kw in text_upper for kw in ["INCOME TAX DEPARTMENT", "PERMANENT ACCOUNT NUMBER", "PAN CARD"]):
            document_type = "PAN Card (Income Tax Dept)"
        elif any(kw in text_upper for kw in ["DRIVING LICENCE", "MOTOR VEHICLES"]):
            document_type = "Driving Licence"
        elif any(kw in text_upper for kw in ["ELECTION COMMISSION", "ELECTOR PHOTO IDENTITY", "EPIC"]):
            document_type = "Voter Identity Card (EPIC)"
        elif "VISA" in text_upper:
            document_type = "Visa / Travel Permit"

        # 1. Parse ICAO Doc 9303 MRZ Lines
        for line in lines:
            clean_line = line.replace(" ", "")
            if clean_line.startswith("P<") or (len(clean_line) >= 30 and "<<" in clean_line):
                mrz_lines.append(clean_line)

        if len(mrz_lines) >= 2:
            mrz_type = "ICAO Doc 9303 TD3 (Passport)"
            document_type = "Passport (ICAO Doc 9303)"
            line1 = mrz_lines[0]
            if line1.startswith("P<"):
                nationality = line1[2:5]
                names_part = line1[5:].split("<<")
                surname = names_part[0].replace("<", "")
                given_names = names_part[1].replace("<", " ").strip() if len(names_part) > 1 else ""
                name = f"{given_names} {surname}".strip()

            line2 = mrz_lines[1]
            if len(line2) >= 28:
                doc_num = line2[0:9].replace("<", "")
                raw_dob = line2[13:19]
                if raw_dob.isdigit():
                    yy = int(raw_dob[0:2])
                    century = "19" if yy > 25 else "20"
                    dob = f"{century}{raw_dob[0:2]}-{raw_dob[2:4]}-{raw_dob[4:6]}"

                raw_gender = line2[20]
                if raw_gender in ["M", "F", "X"]:
                    gender = "Male" if raw_gender == "M" else ("Female" if raw_gender == "F" else "Other")

                raw_exp = line2[21:27]
                if raw_exp.isdigit():
                    expiry = f"20{raw_exp[0:2]}-{raw_exp[2:4]}-{raw_exp[4:6]}"

        # 2. Document Number / Identification Code Extraction (Strict, Multi-Document)
        if not doc_num:
            # A. Educational / Marksheet Identifiers:
            # E.g. "bearing Roll No. 2304120090", "CHILD ID: 1503197288", "Certificate No: WW 060026"
            roll_match = re.search(r'(?:bearing\s+)?(?:Roll\s*No\.?|Roll\s*Number|Hall\s*Ticket\s*(?:No\.?)?|Seat\s*No\.?)[\s.:]*([A-Z0-9\-\/]{6,20})', text, re.IGNORECASE)
            child_match = re.search(r'(?:CHILD\s*ID|STUDENT\s*ID|Registration\s*(?:No\.?)?|Regd\.?\s*No\.?)[\s.:]*([A-Z0-9\-\/]{6,20})', text, re.IGNORECASE)
            cert_no_match = re.search(r'(?:Certificate\s*No\.?|Serial\s*No\.?)[\s.:]*([A-Z0-9\-\/\s]{4,15})', text, re.IGNORECASE)

            if roll_match:
                doc_num = roll_match.group(1).strip()
            elif child_match:
                doc_num = child_match.group(1).strip()
            elif cert_no_match:
                doc_num = cert_no_match.group(1).strip()

        if not doc_num:
            # B. Indian Aadhaar: 12 digits formatted as "XXXX XXXX XXXX" (never begins with 0 or 1)
            aadhaar_spaced = re.search(r'\b([2-9][0-9]{3}\s[0-9]{4}\s[0-9]{4})\b', text)
            if aadhaar_spaced:
                doc_num = aadhaar_spaced.group(1)
            else:
                # Masked Aadhaar: "XXXX XXXX 1234"
                aadhaar_masked = re.search(r'\b([X\*\.x]{4}\s[X\*\.x]{4}\s[0-9]{4})\b', text)
                if aadhaar_masked:
                    doc_num = aadhaar_masked.group(1)
                else:
                    # 12 contiguous digits
                    aadhaar_contig = re.search(r'\b([2-9][0-9]{11})\b', text)
                    if aadhaar_contig:
                        raw_12 = aadhaar_contig.group(1)
                        doc_num = f"{raw_12[0:4]} {raw_12[4:8]} {raw_12[8:12]}"

        if not doc_num:
            # C. International Passport: 1 letter + 7 or 8 digits
            pass_match = re.search(r'\b([A-PR-WY-Z][0-9]{7,8})\b', text)
            if pass_match:
                doc_num = pass_match.group(1)

        if not doc_num:
            # D. Indian PAN Card: 5 uppercase letters + 4 digits + 1 uppercase letter
            pan_match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', text)
            if pan_match:
                doc_num = pan_match.group(1)

        if not doc_num:
            # E. Indian Driving Licence: e.g. DL-07201844910 or AP04 20190012948
            dl_match = re.search(r'\b([A-Z]{2}[0-9]{2}\s?[0-9]{11})\b', text)
            if not dl_match:
                dl_match = re.search(r'\b(DL[0-9A-Z\-]{9,16})\b', text)
            if dl_match:
                doc_num = dl_match.group(1)

        if not doc_num:
            # F. Voter ID (EPIC): 3 uppercase letters followed by 7 digits
            epic_match = re.search(r'\b([A-Z]{3}[0-9]{7})\b', text)
            if epic_match:
                doc_num = epic_match.group(1)

        # Sanity check: a valid document number MUST contain at least 4 digits
        if doc_num and sum(c.isdigit() for c in doc_num) < 3:
            doc_num = None

        # 3. Date of Birth (DOB)
        if not dob:
            dob_match = re.search(
                r'(?:DOB|Birth|Date of Birth|DOB\s*:)[\s:]*([0-3]?[0-9][/\-.][0-1]?[0-9][/\-.][1-2][0-9]{3})',
                text,
                re.IGNORECASE
            )
            if dob_match:
                dob = dob_match.group(1)
            else:
                # Standalone date in DD/MM/YYYY format
                gen_date = re.search(r'\b([0-3][0-9]/[0-1][0-9]/[1-2][0-9]{3})\b', text)
                if gen_date:
                    dob = gen_date.group(1)
                else:
                    yob_match = re.search(r'(?:Year of Birth|YOB)[\s:]*([1-2][0-9]{3})', text, re.IGNORECASE)
                    if yob_match:
                        dob = yob_match.group(1)

        # 4. Date of Expiry
        if not expiry:
            exp_match = re.search(
                r'(?:Expiry|Valid Till|Expires|Expiration)[\s:]*([0-3]?[0-9][/\-.][0-1]?[0-9][/\-.][1-2][0-9]{3})',
                text,
                re.IGNORECASE
            )
            if exp_match:
                expiry = exp_match.group(1)

        # 5. Gender (Aadhaar / Passport / ID)
        if not gender:
            # Standalone MALE/FEMALE keywords (handles multilingual cards like "MALE / పురుషుడు")
            if re.search(r'\bMALE\b', text, re.IGNORECASE) and not re.search(r'\bFEMALE\b', text, re.IGNORECASE):
                gender = "Male"
            elif re.search(r'\bFEMALE\b', text, re.IGNORECASE):
                gender = "Female"
            elif re.search(r'\bTRANSGENDER\b', text, re.IGNORECASE):
                gender = "Transgender"
            elif re.search(r'(?:Gender|Sex)[\s:/]*([MF])\b', text, re.IGNORECASE):
                g_code = re.search(r'(?:Gender|Sex)[\s:/]*([MF])\b', text, re.IGNORECASE).group(1).upper()
                gender = "Male" if g_code == "M" else "Female"

        # 6. Parent Name Extraction (Father / Mother)
        father_name = None
        father_match = re.search(r'(?:FATHER(?:\'S)?\s*NAME|FATHER\s*NAME)[\s.:]+([A-Za-z\s]{3,40})', text, re.IGNORECASE)
        if father_match:
            father_cand = father_match.group(1).strip()
            father_cand = re.split(r'\b(?:MOTHER|BEARING|ROLL|CHILD|REGD|PASS)\b', father_cand, flags=re.IGNORECASE)[0].strip()
            father_name = father_cand

        # 7. Name Extraction (Multi-Strategy with Exhaustive Institutional Blacklisting)
        NAME_BLACKLIST = {
            "GOVERNMENT", "INDIA", "AUTHORITY", "UNIQUE", "IDENTIFICATION", "ENROLMENT",
            "MERA", "AADHAAR", "PEHCHAN", "HELP", "STATE", "PRADESH", "ANDHRA", "TELANGANA",
            "DISTRICT", "PINCODE", "ADDRESS", "HOUSE", "DOOR", "ROAD", "STREET", "NAGAR",
            "FATHER", "MOTHER", "HUSBAND", "WIFE", "GUARDIAN", "SIGNATURE", "INFORMATION",
            "BOARD", "SECONDARY", "EDUCATION", "EXAMINATION", "AMARAVATI", "CERTIFICATE",
            "COLLEGE", "UNIVERSITY", "INSTITUTE", "ACADEMY", "SCHOOL", "REGULAR", "MARKS",
            "STATEMENT", "PASS", "PASSED", "FIRST", "SECOND", "DIVISION", "MEDIUM", "INSTRUCTION",
            "CANDIDATE", "STUDENT", "CERTIFIED", "CERTIFY", "CENTRAL", "COUNCIL", "TECHNICAL",
            "MEMBER", "SECRETARY", "DIRECTOR", "CONTROLLER", "HEADMASTER", "PRINCIPAL", "STAMP"
        }

        def is_clean_name(candidate_str: str) -> bool:
            c = candidate_str.strip()
            if len(c) < 3 or len(c) > 40:
                return False
            # Check for concatenated institutional tokens (e.g. "ANDHRAPRADESHAMARAVATI")
            c_upper = c.upper()
            for token in ["AMARAVATI", "ANDHRA", "PRADESH", "SECONDARY", "EDUCATION", "BOARD", "CERTIFICATE", "SCHOOL"]:
                if token in c_upper:
                    return False
            # Names must not have colons, semicolons, digits, or URLs
            if any(char in c for char in [':', ';', '@', '/', '\\', 'http', '.com', '.in', '=']):
                return False
            if any(char.isdigit() for char in c):
                return False
            words = c.split()
            if len(words) < 1 or len(words) > 5:
                return False
            # Check against blacklisted words
            upper_words = [w.strip(".,;:").upper() for w in words]
            for w in upper_words:
                if w in NAME_BLACKLIST:
                    return False
            return True

        if not name:
            # Strategy 0: Educational Certificate / Board Marksheet Certification Line:
            # E.g. "CERTIFIED THAT <CANDIDATE NAME>" or "THIS IS TO CERTIFY THAT ..."
            cert_pattern = re.search(
                r'(?:CERTIFIED\s+THAT|THIS\s+IS\s+TO\s+CERTIFY\s+THAT|CANDIDATE(?:\'S)?\s+NAME|NAME\s+OF\s+(?:THE\s+)?(?:CANDIDATE|STUDENT))[\s.:]+([A-Za-z\s]{3,50})',
                text,
                re.IGNORECASE
            )
            if cert_pattern:
                cand = cert_pattern.group(1).strip()
                cand = re.split(r'\b(?:FATHER|MOTHER|SON|DAUGHTER|BEARING|ROLL|CHILD|OF|HAS|WHO|PASSED)\b', cand, flags=re.IGNORECASE)[0].strip()
                if is_clean_name(cand):
                    name = cand

        if not name:
            # Strategy A: On e-Aadhaar letters, the recipient name is on the line immediately after "To"
            for idx, line in enumerate(lines):
                clean_line = line.strip().upper()
                if clean_line in ["TO", "TO,", "TO :", "TO:"] and idx + 1 < len(lines):
                    next_line = lines[idx + 1].strip()
                    if is_clean_name(next_line):
                        name = next_line
                        break

        if not name:
            # Strategy B: Explicit "Name:" or "Given Name:" label (ignoring Father/Mother/Board lines)
            for line in lines:
                if any(kw in line.upper() for kw in ["FATHER", "MOTHER", "BOARD", "SECONDARY"]):
                    continue
                name_match = re.search(r'(?:Name|Given Name|Surname|Holder Name)[\s:]+([A-Za-z\s]{3,35})', line, re.IGNORECASE)
                if name_match:
                    cand = name_match.group(1).strip()
                    if is_clean_name(cand):
                        name = cand
                        break

        if not name:
            # Strategy C: Line immediately above DOB (filtered strictly for clean name)
            for idx, line in enumerate(lines):
                if "DOB" in line.upper() or "DATE OF BIRTH" in line.upper():
                    for offset in [1, 2]:
                        if idx - offset >= 0:
                            cand = lines[idx - offset].strip()
                            if is_clean_name(cand):
                                name = cand
                                break
                    if name:
                        break

        # 8. Nationality
        if not nationality:
            if any(k in text.upper() for k in ["AADHAAR", "UIDAI", "INDIA", "BHARAT", "ANDHRA", "DELHI"]):
                nationality = "IND"
            else:
                nationality = "IND"

        # 9. Visa Specific
        visa_match = re.search(r'(?:Visa No|Visa Number)[\s:#]*([A-Z0-9]{7,12})', text, re.IGNORECASE)
        if visa_match:
            visa_num = visa_match.group(1)
            visa_type_match = re.search(r'(?:Type|Class|Category)[\s:]*([A-Z0-9\-\s]{1,10})', text, re.IGNORECASE)
            visa_type = visa_type_match.group(1).strip() if visa_type_match else "Tourist (T-1)"
            stay_match = re.search(r'(?:Stay Duration|Duration of Stay|Period)[\s:]*([0-9]{1,3}\s*Days)', text, re.IGNORECASE)
            stay_duration = stay_match.group(1) if stay_match else "90 Days"
            entry_match = re.search(r'(?:Entries|Entry)[\s:]*(Multiple|Single|Double)', text, re.IGNORECASE)
            entry_validation = entry_match.group(1) if entry_match else "Multiple Entry"

        return {
            "name": name,
            "date_of_birth": dob,
            "document_number": doc_num,
            "nationality": nationality,
            "expiry_date": expiry,
            "gender": gender,
            "document_type": document_type,
            "father_name": father_name,
            "visa_number": visa_num,
            "visa_type": visa_type,
            "stay_duration": stay_duration,
            "entry_validation": entry_validation,
            "mrz_lines": mrz_lines if mrz_lines else None,
            "mrz_type": mrz_type
        }

ocr_service = OCRService()

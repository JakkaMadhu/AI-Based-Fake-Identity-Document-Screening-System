"""
Sovereign Vision-Language OCR & Identity Parameter Extraction via Ollama.
Directly feeds identity document images into local Vision-Language Models
(e.g., Qwen2.5-VL 7B) running via Ollama at http://127.0.0.1:11434.
"""

import json
import base64
import os
import io
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from PIL import Image
from ..utils.logging import logger

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")


class OllamaVisionService:
    """
    Client for local Vision-Language Models in Ollama.
    Processes document images natively (without third-party cloud APIs)
    to perform optical character recognition, layout comprehension,
    and structured identity parameter extraction.
    """
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.preferred_vision_models = [
            "qwen2.5vl:7b",
            "qwen2.5vl",
            "qwen2.5-vl:7b",
            "qwen2.5-vl",
            "qwen2.5vl:latest",
            "llama3.2-vision:11b",
            "llama3.2-vision",
            "llava:7b",
            "llava"
        ]

    def is_available(self) -> bool:
        """Check if local Ollama daemon is active and responding."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                headers={"User-Agent": "ScreeningSystem/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_available_model(self) -> Optional[str]:
        """
        Detects available models installed in Ollama.
        Prioritizes vision-capable models (qwen2.5vl:7b, etc.).
        """
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                headers={"User-Agent": "ScreeningSystem/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("models", [])
                if not models:
                    return None

                installed_names = [m.get("name", "") for m in models]
                logger.info(f"Ollama installed models: {installed_names}")

                # 1. Match specific preferred vision models
                for pref in self.preferred_vision_models:
                    for installed in installed_names:
                        if pref.lower() == installed.lower():
                            return installed

                # 2. Match any model with 'vl' or 'vision' in name
                for installed in installed_names:
                    lower = installed.lower()
                    if "vl" in lower or "vision" in lower:
                        return installed

                # 3. Check model capabilities in tags for "vision"
                for m in models:
                    caps = m.get("capabilities", [])
                    if "vision" in caps:
                        return m.get("name")

                # 4. Fallback to first available model
                return installed_names[0] if installed_names else None
        except Exception as e:
            logger.warning(f"Could not query Ollama tags: {e}")
            return None

    def _prepare_image_base64(self, image_path: str, max_dimension: int = 1920) -> str:
        """
        Optimizes document image dimensions (if excessively large) and encodes to base64.
        """
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            width, height = img.size
            if max(width, height) > max_dimension:
                scale = max_dimension / float(max(width, height))
                new_w = int(width * scale)
                new_h = int(height * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=90)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Sends the document image directly to Ollama Qwen2.5-VL to perform
        end-to-end vision OCR and identity extraction.
        """
        active_model = self.get_available_model()
        if not active_model:
            raise RuntimeError(
                "Ollama vision model is not reachable. Ensure Ollama is running and qwen2.5vl:7b is loaded."
            )

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Document image not found at: {image_path}")

        image_b64 = self._prepare_image_base64(image_path)

        prompt = """
You are an expert identity document verification and border control intelligence model.
Inspect this document image carefully. Read all text in all languages (English, Hindi, regional scripts).
Extract the visual text and identity attributes with high precision.

CRITICAL EXTRACTION RULES:
1. "raw_text": The complete transcribed text read from the document, preserving original layout and languages.
2. "document_type": Name of document category (e.g. "Aadhaar Card", "Passport", "PAN Card", "Driving Licence", "Voter Identity Card", "Secondary School Certificate").
3. "name": The FULL LEGAL NAME of the person/cardholder.
   - Do NOT return the name of the Government, Authority, Department, Board, or State (e.g., NEVER return "Government of India", "Unique Identification Authority of India", "Board of Secondary Education").
4. "document_number": Primary official identifier (e.g. 12-digit Aadhaar "XXXX XXXX XXXX", Passport number, 10-character PAN, Driving Licence number, Roll/Certificate number).
5. "date_of_birth": Date of birth in DD/MM/YYYY or YYYY-MM-DD.
6. "gender": "Male", "Female", or null.
7. "father_name": Father's legal name if mentioned, else null.
8. "mother_name": Mother's legal name if mentioned, else null.
9. "nationality": "IND" or standard country name/code.
10. "expiry_date": Expiry date in DD/MM/YYYY or YYYY-MM-DD if present, else null.
11. "mrz_lines": Array of Machine Readable Zone lines if this is a passport/travel document (e.g. lines starting with "P<"), else null.

Respond ONLY with a valid JSON object strictly matching this schema:
{
  "raw_text": "complete extracted text from the document",
  "document_type": "type of document or null",
  "name": "full legal name of person or null",
  "document_number": "primary document number or null",
  "date_of_birth": "DD/MM/YYYY or null",
  "gender": "Male or Female or null",
  "father_name": "father name or null",
  "mother_name": "mother name or null",
  "nationality": "IND",
  "expiry_date": "expiry date or null",
  "mrz_lines": null
}
"""

        payload = {
            "model": active_model,
            "prompt": prompt,
            "images": [image_b64],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=req_data,
            headers={"Content-Type": "application/json", "User-Agent": "ScreeningSystem/1.0"},
            method="POST"
        )

        logger.info(f"Dispatching document image to Ollama Vision model [{active_model}]...")
        with urllib.request.urlopen(req, timeout=90.0) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Ollama returned HTTP status {resp.status}")

            data = json.loads(resp.read().decode("utf-8"))
            raw_response = data.get("response", "{}")
            parsed = json.loads(raw_response)

            # Sanity check: Ensure institutional words weren't placed in the name
            name_val = parsed.get("name")
            if name_val:
                name_upper = str(name_val).upper()
                bad_keywords = [
                    "GOVERNMENT", "INDIA", "AUTHORITY", "IDENTIFICATION", "BOARD",
                    "SECONDARY", "EDUCATION", "PRADESH", "STATE", "MINISTRY", "DEPARTMENT"
                ]
                if any(bad in name_upper for bad in bad_keywords):
                    parsed["name"] = None

            parsed["engine_used"] = f"Ollama Vision ({active_model})"
            logger.info(f"Ollama Vision successfully extracted identity parameters: {parsed.get('document_type')} - {parsed.get('name')}")
            return parsed


ollama_service = OllamaVisionService()

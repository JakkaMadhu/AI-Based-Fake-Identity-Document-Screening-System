"""
Local Ollama AI Model Integration for Document Identity Parameter Extraction.
Connects to local Ollama instance (e.g., Qwen2, Llama3, etc.) at http://127.0.0.1:11434
to perform zero-shot, air-gapped identity parameter extraction from raw OCR text.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from ..utils.logging import logger

OLLAMA_BASE_URL = "http://127.0.0.1:11434"


class OllamaService:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.preferred_models = [
            "qwen2:4b", "qwen2", "qwen2.5:3b", "qwen2.5:7b", "qwen2.5", 
            "llama3.2:3b", "llama3.2", "llama3", "mistral", "phi3"
        ]

    def is_available(self) -> bool:
        """Check if local Ollama daemon is active and responding."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", headers={"User-Agent": "ScreeningSystem/1.0"})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def get_available_model(self) -> Optional[str]:
        """Detects available installed models in Ollama, matching preferred models first."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", headers={"User-Agent": "ScreeningSystem/1.0"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                installed_models = [m.get("name", "") for m in data.get("models", [])]
                if not installed_models:
                    return None

                logger.info(f"Ollama installed models: {installed_models}")

                # 1. Match preferred models
                for pref in self.preferred_models:
                    for installed in installed_models:
                        if pref.lower() in installed.lower():
                            return installed

                # 2. Match any qwen or llama
                for installed in installed_models:
                    if "qwen" in installed.lower() or "llama" in installed.lower():
                        return installed

                # 3. Fallback to first available model
                return installed_models[0]
        except Exception as e:
            logger.warning(f"Could not query Ollama tags: {e}")
            return None

    def extract_identity_entities(self, raw_ocr_text: str, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Sends raw OCR character stream to local Ollama model to extract identity parameters.
        Returns validated structured JSON or None if Ollama is unavailable.
        """
        if not raw_ocr_text or len(raw_ocr_text.strip()) < 15:
            return None

        active_model = model_name or self.get_available_model()
        if not active_model:
            logger.info("Ollama daemon not reachable or no models installed. Skipping local LLM pass.")
            return None

        prompt = f"""
You are a border security inspection intelligence model.
Analyze the following raw Optical Character Recognition (OCR) text extracted from an official identity or educational document (e.g. Secondary School Certificate, Aadhaar, Passport, PAN, Driving Licence).

CRITICAL INSTRUCTIONS:
1. "name": The FULL LEGAL NAME of the student/traveler/candidate.
   - For educational certificates, extract the person name certified (e.g. after 'CERTIFIED THAT', 'THIS IS TO CERTIFY THAT', or preceding father/mother names).
   - NEVER return the name of the Board, Government, State, School, or Authority (e.g. DO NOT return 'BOARD OF SECONDARY EDUCATION' or 'ANDHRA PRADESH' or 'AMARAVATI').
   - CRITICAL NAME NORMALIZATION:
     * Official document scans frequently suffer from OCR watermark bleeding where background security text, guilloche patterns, or repeating watermark letters merge into the foreground name.
     * Autocorrect and clean any watermark fragments, trailing security words, or OCR character noise from the person's legal name using standard real-world naming conventions and cross-referencing with the Father/Mother/Family surname. Output only the clean, authentic person name without background artifacts.
2. "document_number": Primary identification code. For school certificates, this is the Roll Number (e.g. '2304120090') or Child ID (e.g. '1503197288'). For Aadhaar, 12 digits. For Passport, 8-9 chars.
3. "father_name": Father's legal name if mentioned.
4. "mother_name": Mother's legal name if mentioned.
5. "date_of_birth": Date of birth in DD/MM/YYYY or YYYY-MM-DD.
6. "gender": Male, Female, or null.
7. "document_type": E.g. "Secondary School Certificate", "Aadhaar Card", "Passport", "PAN Card", etc.
8. "nationality": "IND" or 3-letter ISO code.

RAW OCR TEXT STREAM:
\"\"\"
{raw_ocr_text}
\"\"\"

Respond with ONLY a valid JSON object matching this schema:
{{
  "name": "Full legal name of the person or null",
  "document_number": "Roll No, Child ID, or ID number or null",
  "father_name": "Father's name or null",
  "mother_name": "Mother's name or null",
  "date_of_birth": "DD/MM/YYYY or null",
  "gender": "Male or Female or null",
  "document_type": "Name of document category",
  "nationality": "IND"
}}
"""

        payload = {
            "model": active_model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for deterministic extraction
                "top_p": 0.9
            }
        }

        try:
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=req_data,
                headers={"Content-Type": "application/json", "User-Agent": "ScreeningSystem/1.0"},
                method="POST"
            )

            logger.info(f"Dispatching OCR text ({len(raw_ocr_text)} chars) to local Ollama model [{active_model}]...")
            with urllib.request.urlopen(req, timeout=25.0) as resp:
                if resp.status == 200:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    raw_response = resp_data.get("response", "{}")
                    parsed_json = json.loads(raw_response)
                    logger.info(f"Ollama [{active_model}] extracted fields: {parsed_json}")
                    return parsed_json
        except urllib.error.URLError as ue:
            logger.warning(f"Ollama connection error: {ue.reason}")
        except Exception as e:
            logger.warning(f"Ollama inference failed: {e}")

        return None


ollama_service = OllamaService()

# AI Border Screening System — High-Performance Asynchronous FastAPI Core

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x%20%2B%20CUDA-EE4C2C.svg)](https://pytorch.org/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20Mode-003B57.svg)](https://sqlite.org/)
[![Cryptography](https://img.shields.io/badge/Ledger-SHA--256%20Chained-F7931A.svg)]()

The backend service is an enterprise-grade, asynchronous microservice built on **FastAPI**, **PyTorch**, **Ollama**, and an immutable **SQLite Cryptographic Ledger**. It coordinates deep convolutional forensics, local vision-language OCR, facial biometric matching with motion-blur diagnostics, a 5-factor mathematical risk engine, and persistent audit trail generation.

---

## Table of Contents
1. [Architecture & Concurrency Model](#architecture--concurrency-model)
2. [Deep Dive: Core Services & Algorithmic Engines](#deep-dive-core-services--algorithmic-engines)
   - [2.1 Decision Service (`decision_service.py`)](#21-decision-service-decisionservicepy)
   - [2.2 Biometric Face Service (`face_service.py`)](#22-biometric-face-service-faceservicepy)
   - [2.3 Deep Forensic ML Service (`ml_service.py`)](#23-deep-forensic-ml-service-mlservicepy)
   - [2.4 Vision-Language OCR & Ollama Client (`ocr_service.py` & `ollama_service.py`)](#24-vision-language-ocr--ollama-client-ocrservicepy--ollamaservicepy)
   - [2.5 Forensic Image & Document Processing (`image_service.py` & `document_converter.py`)](#25-forensic-image--document-processing-imageservicepy--documentconverterpy)
   - [2.6 Cryptographic Hash-Chained Ledger (`sqlite_store.py`)](#26-cryptographic-hash-chained-ledger-sqlitestorepy)
3. [Complete REST API Specification](#complete-rest-api-specification)
4. [Installation & Local Setup](#installation--local-setup)
5. [Configuration & Environment Variables](#configuration--environment-variables)
6. [Testing & Verification](#testing--verification)

---

## Architecture & Concurrency Model

The backend is engineered for high throughput and resilient non-blocking I/O:
- **Asynchronous Event Loop**: Fast, non-blocking routing for file uploads, database queries, and inter-service HTTP requests.
- **Thread Pool Delegation (`asyncio.to_thread`)**: Heavy deep-learning inferences (PyTorch TruFor tensors, FaceNet embeddings) run in thread pools to prevent blocking the asyncio event loop.
- **Persistent Local Caching**: Uploaded files and generated forensic heatmap overlays are stored in an organized local static directory (`uploads/`) with immediate URI mapping.
- **Thread-Safe SQLite Singleton**: SQLite database queries run under thread-safe synchronization locks, utilizing WAL mode for maximum concurrency.

---

## Deep Dive: Core Services & Algorithmic Engines

### 2.1 Decision Service (`decision_service.py`)

The decision engine eliminates subjective guesswork by combining a **5-Factor Continuous Mathematical Formula** with **Deterministic Hard Overrides**.

#### 1. The 5-Factor Weighted Formula
$$\text{Risk}_{\text{weighted}} = 0.30 \times F_{\text{face}} + 0.30 \times F_{\text{forgery}} + 0.20 \times F_{\text{ocr}} + 0.10 \times F_{\text{image}} + 0.10 \times F_{\text{rules}}$$

| Factor | Weight | Evaluation Criteria | Normal Range |
|:---|:---:|:---|:---:|
| **$F_{\text{face}}$ (Biometric)** | **30%** | Normalized Euclidean embedding distance ($D$). If $D \le 0.85 \implies 0$. If $D > 1.10 \implies 100$. | $0 - 100$ |
| **$F_{\text{forgery}}$ (Deep Forensic)** | **30%** | TruFor CNN anomaly probability scaled directly to percentage. | $0 - 100$ |
| **$F_{\text{ocr}}$ (Text & Integrity)** | **20%** | Field completeness (Name, DOB, Doc#) and OCR character clarity penalties. | $0 - 100$ |
| **$F_{\text{image}}$ (Compression & Quality)**| **10%** | Error Level Analysis (ELA) variance, metadata editing software traces. | $0 - 100$ |
| **$F_{\text{rules}}$ (ICAO & Watchlist)** | **10%** | ICAO 9303 checksum failures, temporal expiration status, security watchlist. | $0 - 100$ |

#### 2. Deterministic Hard Overrides
To ensure national security and prevent catastrophic edge cases from being diluted by averaging, the system enforces **deterministic overrides**:
1. **Biometric Impostor Override**: If Euclidean distance $D > 1.10$ and the selfie is confirmed clear, the verdict immediately locks to **`Suspicious`** with a minimum Risk Score of $85/100$.
2. **Spliced Document Override**: If TruFor forgery probability $P_{\text{fake}} \ge 0.70$, the verdict immediately locks to **`Suspicious`** (Risk Score $\ge 85$).
3. **ICAO 9303 Checksum Violation**: If the Machine Readable Zone (MRZ) 7-3-1 check digit does not compute, the document is flagged as **`Suspicious`** (Risk Score $\ge 85$).
4. **Expired Credential Override**: If the expiration date is in the past, the verdict is flagged for review.
5. **Blur / Clarity Fallback**: If the live selfie fails clarity thresholds, it triggers `FACE_NOT_CLEAR` with a dedicated directive rather than penalizing the traveler as an impostor.

---

### 2.2 Biometric Face Service (`face_service.py`)

Performs automated 1:1 facial biometric cross-matching between the photo inside the physical credential and the live traveler capture.

- **Detector (MTCNN)**:
  - Multi-task Cascaded Convolutional Networks detect face bounding boxes and 5 facial keypoints (left eye, right eye, nose tip, left mouth corner, right mouth corner).
  - Normalizes crop dimensions to $160 \times 160$ RGB pixels.
- **Embedding Network (FaceNet / Inception-ResNet-V1)**:
  - Pretrained on VGGFace2, generating a 512-dimensional vector $\mathbf{v} \in \mathbb{R}^{512}$ normalized to unit length ($\|\mathbf{v}\|_2 = 1$).
- **Euclidean Distance Matching**:
  $$D(\mathbf{v}_1, \mathbf{v}_2) = \sqrt{\sum_{i=1}^{512} (v_{1,i} - v_{2,i})^2}$$
- **Clarity & Motion Blur Diagnostics**:
  - Computes Laplacian variance $\sigma^2_{\Delta} = \text{Var}(\nabla^2 I)$ and Sobel edge energy $\bar{G} = \frac{1}{N}\sum \sqrt{G_x^2 + G_y^2}$.
  - If energy $< 25.0$, flags `error_code="FACE_NOT_CLEAR"` and advises immediate retake with steady camera.

---

### 2.3 Deep Forensic ML Service (`ml_service.py`)

Implements the **TruFor** (True Forensics) state-of-the-art neural architecture for digital forgery detection and localization:
- **Dual-Stream Extraction**: Combines high-resolution RGB image tensors with a convolutional Noiseprint extractor that isolates sensor pattern noise residuals (PRNU).
- **Pixel-Level Localization**: Employs a fully convolutional decoder that produces a spatial confidence matrix $[H, W]$ representing local anomaly probabilities.
- **Heatmap & Overlay Generation**:
  - Automatically transforms raw anomaly matrices into colorized heatmaps using OpenCV colormaps (`COLORMAP_JET`).
  - Generates a composite blend: $\alpha \cdot \text{Document} + (1 - \alpha) \cdot \text{Heatmap}$ and exposes it via `/uploads/` for real-time visual inspection in the frontend.

---

### 2.4 Vision-Language OCR & Ollama Client (`ocr_service.py` & `ollama_service.py`)

- **Sovereign Local Inference**: Connects to an on-premise Ollama instance hosting **Qwen2.5-VL 7B** via HTTP POST `/api/generate`.
- **Structured Schema Prompting**: Constrains the model to return valid JSON with strict key definitions:
  ```json
  {
    "document_type": "PASSPORT | NATIONAL_ID | DRIVING_LICENSE | VISA",
    "document_number": "string",
    "name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "expiry_date": "YYYY-MM-DD",
    "nationality": "ISO-3 code",
    "gender": "M | F | X",
    "mrz_lines": ["string", "string"]
  }
  ```
- **ICAO Doc 9303 Checksum Engine**:
  - Validates MRZ TD1 (3-line ID card), TD2 (2-line visa), and TD3 (2-line passport).
  - Implements cyclic weights $(7, 3, 1)$ modulo 10:
    $$\text{CheckDigit} = \left(\sum_{k=0}^{n-1} c_k \cdot w_{k \pmod 3}\right) \pmod{10}$$

---

### 2.5 Forensic Image & Document Processing (`image_service.py` & `document_converter.py`)

- **Multi-Format Ingestion**: Uses `PyMuPDF` (`fitz`) to rasterize incoming PDF travel permits, e-Visas, and multi-page documents at 300 DPI into lossless RGB arrays.
- **Error Level Analysis (ELA)**:
  - Re-saves the incoming image at 90% JPEG quality.
  - Computes the absolute pixel difference: $\Delta = |I_{\text{original}} - I_{\text{recompressed}}|$.
  - Scales and analyzes high-frequency error distribution to identify spliced or digitally retouched segments.
- **EXIF Metadata Inspection**: Scans image headers for digital editing software signatures (Adobe Photoshop, GIMP, Canva, CorelDRAW).

---

### 2.6 Cryptographic Hash-Chained Ledger (`sqlite_store.py`)

To guard against insider tampering, every screening record is committed to a **Cryptographic Hash-Chained Blockchain Ledger**:

```text
Genesis Block (index: 0, hash: "0000000000000000000000000000000000000000000000000000000000000000")
       │
       ▼
Block #1 [ doc_id: "doc-1a2b3c4d", status: "Likely Genuine", prev_hash: "0000...", block_hash: "7f8e..." ]
       │
       ▼
Block #2 [ doc_id: "doc-9f8e7d6c", status: "Suspicious",     prev_hash: "7f8e...", block_hash: "3a1c..." ]
       │
       ▼
Block #3 [ doc_id: "doc-5b4a3e2f", status: "Likely Genuine", prev_hash: "3a1c...", block_hash: "b90d..." ]
```

- **Hash Formulation**:
  $$\text{Hash}_i = \text{SHA-256}(\text{Index}_i \parallel \text{Hash}_{i-1} \parallel \text{DocID}_i \parallel \text{Status}_i \parallel \text{Timestamp}_i)$$
- **Tamper Evidence**: If any row or screening result in the database is modified or deleted by an unauthorized database admin, the cryptographic chain is invalidated and detected immediately.

---

## Complete REST API Specification

### 1. Ingest 2-Step Live Capture
- **Endpoint**: `POST /api/documents/upload-live`
- **Request Body**:
  ```json
  {
    "document_base64": "data:image/jpeg;base64,...",
    "face_base64": "data:image/jpeg;base64,...",
    "filename": "live_scan.jpg"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "document_id": "doc-a82f7c10",
    "filename": "live_scan.jpg",
    "uploaded_at": "2026-09-04T21:15:00Z",
    "status": "uploaded",
    "message": "Live document & face registered successfully.",
    "preview_url": "/uploads/doc-a82f7c10.jpg",
    "face_preview_url": "/uploads/face_doc-a82f7c10.jpg"
  }
  ```

### 2. Execute Screening Pipeline
- **Endpoint**: `POST /api/documents/{document_id}/screen`
- **Response** (`200 OK`):
  ```json
  {
    "document_id": "doc-a82f7c10",
    "filename": "passport.jpg",
    "screening_status": "Likely Genuine",
    "risk_level": "Low Risk",
    "risk_score": 14,
    "genuine_probability": 0.94,
    "forged_probability": 0.06,
    "model_confidence": 0.96,
    "ocr_results": {
      "name": "JOHN DOE",
      "date_of_birth": "1988-04-12",
      "document_number": "P83726194",
      "nationality": "USA",
      "expiry_date": "2030-05-18",
      "document_type": "PASSPORT",
      "mrz_lines": ["P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<", "P837261944USA8804128M3005182<<<<<<<<<<<<<<08"]
    },
    "validation_summary": {
      "mrz_checksum_passed": true,
      "mrz_checksum_details": "ICAO Doc 9303 checksums passed",
      "is_expired": false,
      "expiry_status": "Valid",
      "watchlist_flagged": false
    },
    "tampering_forensics": {
      "trufor_score": 0.06,
      "is_tampered": false,
      "tamper_heatmap_url": "/uploads/heatmap_doc-a82f7c10.jpg",
      "tamper_overlay_url": "/uploads/overlay_doc-a82f7c10.jpg"
    },
    "face_match": {
      "face_verified": true,
      "match_score": 92.5,
      "status": "Biometric Match Confirmed",
      "details": "Euclidean Distance: 0.54 (Threshold: 0.85)",
      "is_face_clear": true
    },
    "ledger_block": {
      "block_index": 42,
      "block_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "previous_hash": "7a35b... ",
      "timestamp": "2026-09-04T21:15:30Z",
      "signature_algorithm": "SHA-256 Hash Chained Ledger",
      "integrity_status": "Verified Immutable Record"
    },
    "risk_breakdown": {
      "face_risk": 0.0,
      "forgery_risk": 6.0,
      "ocr_risk": 0.0,
      "image_risk": 5.0,
      "rule_risk": 0.0,
      "weighted_score": 2.3,
      "overrides_triggered": []
    }
  }
  ```

### 3. Retrieve Historical Screening Log
- **Endpoint**: `GET /api/documents/history?page=1&page_size=10&status=all`
- **Response** (`200 OK`): Paginated list of inspection records with document IDs, risk badges, and SHA-256 block hashes.

---

## Installation & Local Setup

1. **Environment Setup**:
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate   # Linux: source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Launch Development Server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Verify Health**:
   ```bash
   curl http://127.0.0.1:8000/api/health
   ```

---

## Configuration & Environment Variables

Create an optional `.env` file in `backend/` to override default settings:

| Variable | Default Value | Purpose |
|:---|:---|:---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama Vision API host URL |
| `OLLAMA_MODEL` | `qwen2.5-vl:7b` | Model tag for Vision-Language OCR |
| `FACE_MATCH_THRESHOLD` | `0.85` | Euclidean distance cutoff for positive biometric match |
| `TRUFOR_WEIGHTS_PATH` | `trained_models/trufor.pth.tar` | Pretrained TruFor model weights location |
| `DB_PATH` | `screening_system.db` | SQLite database file location |

---

## Testing & Verification

To run automated integration tests across the screening pipeline:
```bash
python test_doc.py
```
This executes the end-to-end flow: file conversion, image ELA, deep TruFor inference, FaceNet biometric distance calculation, and SHA-256 ledger block generation.

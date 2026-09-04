# AI-Powered Autonomous Border Screening & Multi-Modal Identity Verification System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Asynchronous%20Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-EE4C2C.svg)](https://pytorch.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5--VL%207B-black.svg)](https://ollama.com/)
[![React 18](https://img.shields.io/badge/React-18.x%20%7C%20Vite-61DAFB.svg)](https://react.dev/)
[![Blockchain](https://img.shields.io/badge/Blockchain-SHA--256%20Hash--Chained%20Ledger-orange.svg)]()
[![Security](https://img.shields.io/badge/Security-ICAO%20Doc%209303%20Compliant-red.svg)]()

> **Enterprise-Grade Multi-Modal Identity Screening**: Designed for Automated Border Control (e-Gates), high-throughput airport checkpoints, and FinTech KYC onboarding. Integrates Deep Forensic Anomaly Detection, Sovereign Vision-Language OCR, 1:1 Live Biometric Facial Cross-Matching with Motion Blur Diagnostics, a 5-Factor Weighted Risk Engine with Deterministic Hard Overrides, and an Immutable Cryptographic SHA-256 Hash-Chained Blockchain Audit Ledger.

---

## Table of Contents
1. [Executive Overview & Problem Statement](#executive-overview--problem-statement)
2. [End-to-End System Architecture](#end-to-end-system-architecture)
3. [Core Technical Pillars & Pipeline](#core-technical-pillars--pipeline)
   - [3.1 Deep Forensic Tampering Detection (TruFor)](#31-deep-forensic-tampering-detection-trufor)
   - [3.2 Sovereign Vision-Language OCR (Qwen2.5-VL 7B)](#32-sovereign-vision-language-ocr-qwen25-vl-7b)
   - [3.3 ICAO Doc 9303 Checksum Engine (7-3-1 Weighting)](#33-icao-doc-9303-checksum-engine-7-3-1-weighting)
   - [3.4 1:1 Facial Biometric Cross-Matcher (MTCNN + FaceNet)](#34-11-facial-biometric-cross-matcher-mtcnn--facenet)
   - [3.5 Biometric Clarity & Motion Blur Diagnostics](#35-biometric-clarity--motion-blur-diagnostics)
   - [3.6 5-Factor Mathematical Risk Engine & Hard Overrides](#36-5-factor-mathematical-risk-engine--hard-overrides)
   - [3.7 Cryptographic SHA-256 Hash-Chained Blockchain Ledger](#37-cryptographic-sha-256-hash-chained-blockchain-ledger)
4. [Repository Structure](#repository-structure)
5. [Prerequisites & System Requirements](#prerequisites--system-requirements)
6. [Step-by-Step Installation & Quick Start](#step-by-step-installation--quick-start)
   - [Backend Setup (FastAPI)](#1-backend-setup-fastapi)
   - [Ollama Vision Model Setup](#2-ollama-vision-model-setup)
   - [Pretrained Model Weights](#3-pretrained-model-weights)
   - [Frontend Setup (React + Vite)](#4-frontend-setup-react--vite)
7. [API Reference & Microservice Endpoints](#api-reference--microservice-endpoints)
8. [Production Deployment & e-Gate Operational Guide](#production-deployment--e-gate-operational-guide)
9. [Disclaimer](#disclaimer)

---

## Executive Overview & Problem Statement

Modern border authorities and financial institutions face unprecedented challenges from:
1. **Generative AI & Deepfakes**: Sophisticated generative inpainting, neural portrait swaps, and font synthesis that bypass traditional template-matching software.
2. **Physical Tampering & Splicing**: Photo substitution, laser ablation, mechanical erasure, and micro-text alterations on physical passports and visas.
3. **Data Inconsistencies & Synthetic Identities**: Fabricated passport numbers and mismatched check digits hidden within Machine Readable Travel Documents (MRTD).
4. **Substandard Capture in Live Kiosks**: Travelers moving or poorly lit during automated e-Gate capture, causing brittle biometric systems to trigger false rejections or wrongful accusations.
5. **Insider Threat & Log Tampering**: Malicious actors or compromised database administrators altering inspection logs or passing illicit travelers post-factum.

This system addresses each vector through a **cohesive multi-modal defense-in-depth architecture**, combining deep convolutional forensics, local vision-language AI, biometric Euclidean feature matching, deterministic rules, and immutable cryptographic chaining.

---

## End-to-End System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 OPERATOR / TRAVELER INTERFACE                                    │
│       React 18 + Vite SPA | Cyber-Defense Glassmorphic Dashboard | WebRTC Dual-Stream KYC       │
└─────────────────────────────────┬──────────────────────────────────────▲─────────────────────────┘
                                  │ Multipart Form Data                  │ JSON Report & Visual Maps
                                  │ (Document Image/PDF + Live Selfie)   │ (Heatmaps, Crops, Hashes)
┌─────────────────────────────────▼──────────────────────────────────────┴─────────────────────────┐
│                                   FASTAPI ASYNCHRONOUS BACKEND                                   │
│                        High-Performance Asynchronous Microservice Core                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                MULTI-MODAL VERIFICATION PIPELINE                                 │
│                                                                                                  │
│   [1. Ingestion & Preprocessing]                                                                 │
│   ├── PyMuPDF: High-DPI rasterization (PDF/DOCX to lossless RGB)                                 │
│   └── Image Quality: EXIF metadata strip, Error Level Analysis (ELA), CLAHE contrast            │
│                                                                                                  │
│   [2. Deep Forgery Forensics]                                                                    │
│   ├── TruFor Convolutional Architecture: RGB feature maps + Noiseprint residual extraction       │
│   └── Pixel-Level Tampering Localization: Spatial anomaly probability heatmaps & overlay        │
│                                                                                                  │
│   [3. Vision-Language OCR & ICAO Doc 9303 Engine]                                                │
│   ├── Ollama Qwen2.5-VL 7B Vision Model: Structured entity extraction (JSON schema)             │
│   └── ICAO Doc 9303 Checksums: 7-3-1 modulo-10 algorithm for MRZ TD1 / TD2 / TD3                 │
│                                                                                                  │
│   [4. Biometric Cross-Matcher & Clarity Diagnostic]                                              │
│   ├── MTCNN Face Alignment: Dual crop extraction (Credential portrait vs. Live selfie)         │
│   ├── FaceNet (Inception-ResNet-V1): 512-dimensional Euclidean / Cosine embedding distance       │
│   └── Clarity & Blur Evaluator: Laplacian variance & gradient energy (Motion vs. Impostor)       │
│                                                                                                  │
│   [5. 5-Factor Risk Decision Engine with Deterministic Hard Overrides]                           │
│   ├── Mathematical Risk Equation: 30% Face + 30% Forgery + 20% OCR + 10% Image + 10% Rules      │
│   └── Hard Overrides: Splicing >= 0.70 | Impostor Dist > 1.10 | Checksum Failure | Expired Doc  │
│                                                                                                  │
│   [6. Cryptographic Hash-Chained Blockchain Ledger]                                              │
│   ├── SHA-256 Merkle Block: index, timestamp, doc_id, verdict, risk_score, prev_hash, block_hash │
│   └── SQLite Persistent Store: Tamper-evident, zero external node dependencies                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Technical Pillars & Pipeline

### 3.1 Deep Forensic Tampering Detection (TruFor)
Unlike conventional computer vision that inspects semantic image contents, **TruFor** (True Forensics) operates on sub-visual digital camera fingerprints:
- **RGB + Noiseprint Integration**: Combines RGB color features with high-frequency sensor noise residuals (PRNU/noiseprint). When an adversary splices an image, pastes a portrait, or alters text, the local noise pattern breaks.
- **Pixel-Level Localization**: Generates a floating-point spatial confidence map (0.0 to 1.0) pinpointing precisely which region was modified (e.g., photo boundary, date string).
- **Global Forgery Probability**: Evaluates whether the document as a whole contains digital manipulation artifacts.

### 3.2 Sovereign Vision-Language OCR (Qwen2.5-VL 7B)
Rather than relying on legacy rule-based OCR (e.g., Tesseract) or insecure cloud APIs that violate sovereignty laws (GDPR, PII regulations):
- Powered locally by **Qwen2.5-VL 7B** running on-premise through **Ollama**.
- Directly perceives complex document layouts, anti-counterfeiting guilloche patterns, fonts, and multilingual scripts.
- Outputs clean, structured JSON containing: `document_type`, `document_number`, `holder_name`, `date_of_birth`, `expiry_date`, `nationality`, `gender`, and full `mrz_lines`.

### 3.3 ICAO Doc 9303 Checksum Engine (7-3-1 Weighting)
Every official passport and travel document adheres to international ICAO standards:
- **Checksum Calculation**: Parses Machine Readable Zone (MRZ) lines according to ICAO Doc 9303 (TD1, TD2, and TD3 specifications).
- **Weighting Formula**: Applies cyclic weights $7, 3, 1, 7, 3, 1 \dots \pmod{10}$ over alphanumeric fields (Document Number, Date of Birth, Expiration Date).
- **Deterministic Validation**: Any discrepancy between visual text and MRZ checksums immediately indicates forged numbers or altered dates.

### 3.4 1:1 Facial Biometric Cross-Matcher (MTCNN + FaceNet)
Verifies whether the person presenting the document matches the credential photograph:
- **MTCNN (Multi-task Cascaded Convolutional Networks)**: Detects facial landmarks (eyes, nose, mouth corners) on both the ID credential photo and the live traveler selfie, normalizing pose and alignment.
- **Inception-ResNet-V1 (FaceNet)**: Computes a 512-dimensional unit-sphere biometric embedding.
- **Euclidean Distance Metric ($D$)**:
  - $D \le 0.85$: **Genuine Match** (High confidence same person).
  - $0.85 < D \le 1.10$: **Borderline / Low Confidence**.
  - $D > 1.10$: **Biometric Mismatch / Impostor**.

### 3.5 Biometric Clarity & Motion Blur Diagnostics
In automated border control, camera vibration or passenger movement often causes image blur. If an algorithm simply compares a blurry photo, it produces an inflated Euclidean distance and wrongfully accuses a legitimate citizen of impersonation.
- **Laplacian Energy & Gradient Edge Analysis**: Computes image high-frequency energy on the live selfie crop.
- **Clarity Diagnostics**: If gradient energy falls below acceptable threshold ($\le 25.0$), the system flags:
  $$\text{Status: } \mathbf{FACE\_NOT\_CLEAR} \quad (\text{Diagnostic: Motion blur or soft focus})$$
- Instructs the border agent or traveler to hold steady and retake the photo, eliminating false impersonation accusations.

### 3.6 5-Factor Mathematical Risk Engine & Hard Overrides
The system computes an overall risk score using a weighted composite formula balanced by border security experts:

$$R_{\text{weighted}} = 0.30 \times F_{\text{face}} + 0.30 \times F_{\text{forgery}} + 0.20 \times F_{\text{ocr}} + 0.10 \times F_{\text{image}} + 0.10 \times F_{\text{rules}}$$

Where:
- $F_{\text{face}}$: Normalized facial distance risk $(0 - 100)$.
- $F_{\text{forgery}}$: TruFor tampering probability scaled to $(0 - 100)$.
- $F_{\text{ocr}}$: OCR readability and entity completeness $(0 - 100)$.
- $F_{\text{image}}$: Image compression, ELA, and metadata anomaly risk $(0 - 100)$.
- $F_{\text{rules}}$: Watchlist, date logic, and security rule penalties $(0 - 100)$.

#### Deterministic Hard Overrides
A low weighted average must never mask a catastrophic flaw. The engine executes **hard overrides** that immediately force an overall **REJECT (High Risk)**:
1. **Biometric Impostor**: Euclidean distance $D > 1.10$ with clear selfie $\implies$ Forced **REJECT** (Risk Score $\ge 85$).
2. **Synthetic / Spliced Credential**: TruFor forgery probability $P_{\text{fake}} \ge 0.70 \implies$ Forced **REJECT** (Risk Score $\ge 85$).
3. **ICAO 9303 Checksum Violation**: MRZ check digit does not compute $\implies$ Forced **REJECT** (Tampered Credential).
4. **Expired Document**: Document past its validity date $\implies$ Forced **REJECT** / Manual Flag.

### 3.7 Cryptographic SHA-256 Hash-Chained Blockchain Ledger
To counter insider threats and maintain audit compliance for international law enforcement:
- Every screening outcome produces an immutable ledger block containing:
  $$\text{Block Hash} = \text{SHA-256}(\text{index} \parallel \text{prev\_hash} \parallel \text{doc\_id} \parallel \text{verdict} \parallel \text{timestamp})$$
- Blocks are chained back to an immutable **Genesis Block** (`0000...0000`).
- If an adversary accesses the backend database directly and modifies a verdict or risk score, the cryptographic hash chain breaks, immediately exposing the tampering during automated validation.

---

## Repository Structure

```text
AI-Based-Fake-Identity-Document-Screening-System/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── documents.py        # File upload & 2-step live camera endpoints
│   │   │       ├── screening.py        # End-to-end multi-modal screening pipeline
│   │   │       └── history.py          # Paginated audit log & operational stats
│   │   ├── models/
│   │   │   └── schemas.py              # Pydantic schemas (Request/Response contracts)
│   │   ├── services/
│   │   │   ├── decision_service.py     # 5-factor risk engine & hard overrides
│   │   │   ├── document_converter.py   # PyMuPDF PDF-to-image rasterizer
│   │   │   ├── face_service.py         # MTCNN + FaceNet biometrics & blur diagnostics
│   │   │   ├── file_service.py         # Local secure disk storage
│   │   │   ├── image_service.py        # ELA, EXIF metadata, and quality checks
│   │   │   ├── ml_service.py           # TruFor deep forensic classifier & heatmaps
│   │   │   ├── ocr_service.py          # OCR orchestrator & ICAO checksum validator
│   │   │   └── ollama_service.py       # Sovereign Qwen2.5-VL 7B vision client
│   │   ├── storage/
│   │   │   └── sqlite_store.py         # SQLite persistent store & SHA-256 blockchain
│   │   ├── utils/
│   │   │   ├── logging.py              # Structured microservice logging
│   │   │   └── validation.py           # ICAO 7-3-1 check digit algorithms
│   │   └── main.py                     # FastAPI application entrypoint & lifecycle
│   ├── trained_models/
│   │   └── trufor.pth.tar              # Pretrained TruFor neural network weights
│   ├── requirements.txt                # Python backend dependencies
│   └── README.md                       # Backend-specific architecture guide
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUploader.jsx    # Drag-and-drop file ingestion
│   │   │   ├── LiveCameraScanner.jsx   # WebRTC dual-step camera (Document + Face)
│   │   │   ├── Navbar.jsx              # Status header & navigation
│   │   │   ├── ResultCard.jsx          # Executive verdict & 4-checkpoint cockpit
│   │   │   ├── RiskIndicator.jsx       # Color-coded risk meter
│   │   │   ├── ScreeningProgress.jsx   # Multi-stage animated pipeline tracker
│   │   │   └── Sidebar.jsx             # Quick portal navigation
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx           # Operational throughput & activity stats
│   │   │   ├── ScreeningResult.jsx     # Executive inspection result view
│   │   │   └── UploadDocument.jsx      # Unified file & camera ingestion page
│   │   ├── services/
│   │   │   └── api.js                  # Axios REST API client
│   │   ├── App.jsx                     # Route definitions & app shell
│   │   ├── index.css                   # Cyber-Defense Glassmorphism design system
│   │   └── main.jsx                    # React 18 DOM mount point
│   ├── package.json                    # Node.js dependencies
│   ├── vite.config.js                  # Vite configuration & backend proxy
│   └── README.md                       # Frontend-specific architecture guide
│
└── README.md                           # Master system documentation (This file)
```

---

## Prerequisites & System Requirements

| Component | Minimum Specification | Recommended Specification |
|:---|:---|:---|
| **Operating System** | Windows 10/11, Ubuntu 22.04 LTS, macOS | Windows 11 / Linux (Ubuntu 22.04) |
| **CPU** | Intel Core i5 / AMD Ryzen 5 (4+ cores) | Intel Core i7/i9 or AMD Ryzen 7/9 (8+ cores) |
| **GPU** | Optional (CPU fallback supported) | NVIDIA RTX 3060 / 4070+ (CUDA 11.8 / 12.x) |
| **RAM** | 16 GB | 32 GB (Optimal for local 7B Vision Model) |
| **Storage** | 10 GB free disk space | 25 GB SSD (for Ollama models & PyTorch weights) |
| **Python** | Python 3.10 or 3.11 | Python 3.10.12 |
| **Node.js** | Node.js 18.x LTS | Node.js 20.x LTS + npm 10.x |
| **Ollama** | Ollama 0.3.0+ | Ollama latest with `qwen2.5-vl:7b` |

---

## Step-by-Step Installation & Quick Start

### 1. Backend Setup (FastAPI)

1. Clone the repository and navigate to the `backend` directory:
   ```bash
   git clone https://github.com/JakkaMadhu/AI-Based-Fake-Identity-Document-Screening-System.git
   cd AI-Based-Fake-Identity-Document-Screening-System/backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Root: `http://127.0.0.1:8000/`
   - Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
   - ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

### 2. Ollama Vision Model Setup

The system utilizes **Qwen2.5-VL 7B** for sovereign, on-premise vision-language OCR:

1. Download and install Ollama from [https://ollama.com/](https://ollama.com/).
2. Pull the vision-language model:
   ```bash
   ollama pull qwen2.5-vl:7b
   ```
3. Verify that the Ollama service is active:
   ```bash
   curl http://localhost:11434/api/tags
   ```

> **Note**: If Ollama is not installed or offline, the system automatically falls back to secondary regex heuristics to ensure uninterrupted screening continuity.

---

### 3. Pretrained Model Weights

1. Ensure the TruFor model checkpoint exists in:
   ```text
   backend/trained_models/trufor.pth.tar
   ```
2. FaceNet (Inception-ResNet-V1) weights download automatically on first run via `facenet-pytorch` and are cached locally.

---

### 4. Frontend Setup (React + Vite)

1. In a new terminal window, navigate to the `frontend` directory:
   ```bash
   cd AI-Based-Fake-Identity-Document-Screening-System/frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   - Application URL: `http://localhost:5173`
   - Traffic to `/api` and `/uploads` is automatically reverse-proxied to `http://127.0.0.1:8000`.

---

## API Reference & Microservice Endpoints

### Ingestion & Upload Endpoints

| Method | Endpoint | Description | Request Payload | Response Model |
|:---|:---|:---|:---|:---|
| `POST` | `/api/documents/upload` | Upload ID document file (JPG, PNG, PDF) | `multipart/form-data` (`file`) | `DocumentUploadResponse` |
| `POST` | `/api/documents/upload-live` | Ingest WebRTC 2-step scan (ID + Face) | JSON (`document_base64`, `face_base64`) | `DocumentUploadResponse` |

### Screening & Decision Endpoints

| Method | Endpoint | Description | Query / Path Params | Response Model |
|:---|:---|:---|:---|:---|
| `POST` | `/api/documents/{id}/screen` | Execute full multi-modal screening pipeline | `id` (Document ID) | `ScreeningResultResponse` |
| `GET` | `/api/documents/{id}/result` | Fetch completed screening result record | `id` (Document ID) | `ScreeningResultResponse` |

### Operational & Audit Endpoints

| Method | Endpoint | Description | Parameters | Response Model |
|:---|:---|:---|:---|:---|
| `GET` | `/api/documents/history` | Paginated audit log of screened identities | `search`, `status`, `risk_level`, `page`, `page_size` | `PaginatedHistoryResponse` |
| `GET` | `/api/documents/stats` | Dashboard statistics & pass/fail counts | None | `DashboardStatsResponse` |
| `GET` | `/api/health` | Service health & model state verification | None | `HealthCheckResponse` |

---

## Production Deployment & e-Gate Operational Guide

For airport e-Gate or enterprise border deployment:
1. **Containerization**: Deploy backend via Docker with NVIDIA Container Toolkit for GPU acceleration (`nvidia-docker`).
2. **Reverse Proxy & SSL/TLS**: Place behind Nginx or Cloudflare with mutual TLS (mTLS) to secure biometric payloads.
3. **Database Security**: Mount the SQLite file on an encrypted NVMe partition (LUKS/BitLocker) with automated write-ahead logging (WAL) enabled.
4. **Physical Camera Calibration**: For automated e-Gates, calibrate overhead lighting to eliminate specular glare on laminated passport surfaces.

---

## Disclaimer

This software is an advanced identity document screening and biometric verification prototype. It provides automated risk categorization and anomaly detection. Final border admission or citizenship decisions should be verified by authorized human immigration officers in compliance with applicable national legislation and international travel covenants.

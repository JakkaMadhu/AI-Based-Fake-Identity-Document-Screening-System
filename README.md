# AI-Based Identity Document Screening System

A full-stack, academic prototype application for identity document forgery screening, optical character recognition (OCR), and transparent risk assessment.

```text
┌─────────────────────────────────────────────────────────────┐
│                 FRONTEND (React + Vite)                     │
│  • Pages: Login, Dashboard, Upload & Live Camera,           │
│           Screening Result, History                         │
│  • Design: Cybersecurity Dark Theme with Glassmorphism      │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API (JSON / FormData)
┌──────────────────────────────▼──────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  • Routes: /upload, /upload-live, /screen, /result, /history│
│  • Services: File, Image Preprocessing, MobileNetV2, OCR    │
│  • Storage: Zero-DB In-Memory Store (Fast & Lightweight)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
    ┌───────────▼───────────┐     ┌───────────▼───────────┐
    │    MobileNetV2 AI     │     │     OCR Pipeline      │
    │ fake_document_model   │     │ Tesseract / Heuristic │
    │ (.keras + Mock mode)  │     │ (Regex Field Parsing) │
    └───────────────────────┘     └───────────────────────┘
```

---

## Quick Start Guide

### 1. Start the Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
* Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
* Frontend Web App: `http://localhost:5173`

---

## Instructions for Teammates (Plugging in the AI Model)

When your teammates finish training their MobileNetV2 model on **SIDTD** or **IDNet**:

1. Export the trained model as a Keras archive:
   `fake_document_model.keras`
2. Place the file inside:
   `backend/trained_models/fake_document_model.keras`
3. Restart the backend server. The backend will automatically detect and load the model into memory once on startup!

*(Until the file is added, the backend automatically runs in **simulation mode** so the entire full-stack application and live webcam scanner can be tested and demonstrated immediately.)*

---

## System Workflow

1. **Capture / Upload**:
   - Live Webcam scan with rectangular ID card alignment box, OR
   - Drag & drop file upload (`.jpg`, `.jpeg`, `.png`, max 10MB).
2. **Validation**: Verifies file type, dimensions, and image integrity.
3. **Preprocessing**: Resizes to `224×224` and normalizes for MobileNetV2.
4. **AI Vision Classification**: Analyzes micro-textures and tampering boundaries.
5. **OCR Extraction**: Scans visible text and extracts Name, Date of Birth, and Document ID.
6. **Decision & Risk Engine**: Synthesizes probability scores into transparent categories:
   - **Likely Genuine** (Low Risk)
   - **Requires Manual Review** (Medium Risk)
   - **Suspicious** (High Risk)

# AI-Based Identity Document Screening System - Backend

High-performance FastAPI backend service providing document validation, MobileNetV2 AI forgery classification, OCR text extraction, transparent risk decisioning, and an in-memory audit store.

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Optional for real local inference and OCR):*
```bash
pip install tensorflow pytesseract
```

### 2. Start the FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. API Documentation
Once running, open your browser to:
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

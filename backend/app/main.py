from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from .api.routes import documents, screening, history
from .services.ml_service import ml_service
from .utils.logging import logger

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML model into memory once
    logger.info("Initializing AI-Based Document Screening System backend...")
    ml_service.load_model()
    logger.info("System ready to process document screenings.")
    yield
    # Shutdown
    logger.info("Shutting down backend services.")

app = FastAPI(
    title="AI-Based Identity Document Screening System API",
    description="Academic prototype API for document forgery screening, OCR extraction, and risk assessment.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for image previews
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include Routers
app.include_router(documents.router)
app.include_router(screening.router)
app.include_router(history.router)

@app.get("/")
def read_root():
    return {
        "service": "AI-Based Identity Document Screening System",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/documents/upload",
            "upload_live": "POST /api/documents/upload-live",
            "screen": "POST /api/documents/{id}/screen",
            "result": "GET /api/documents/{id}/result",
            "history": "GET /api/documents/history",
            "stats": "GET /api/documents/stats"
        },
        "disclaimer": "Academic prototype only. Does not claim legal authentication of official identity documents."
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": ml_service.is_loaded,
        "using_mock_model": ml_service.using_mock
    }

"""
Document-to-Image Converter Service.
Converts PDF and DOCX files to high-resolution JPEG images (300 DPI)
so the Vision AI pipeline (Qwen2.5-VL, ELA, TruFor) can inspect them visually.
"""

import os
import io
from pathlib import Path
from typing import Tuple
from PIL import Image
from ..utils.logging import logger

UPLOAD_DIR = Path("uploads")


def convert_document_to_image(file_path: str) -> Tuple[str, bool]:
    """
    If the file is a PDF or DOCX, converts page 1 to a 300 DPI JPEG image.
    If it's already an image, returns the original path unchanged.

    Returns: (image_file_path, was_converted)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".jpg", ".jpeg", ".png"):
        return file_path, False

    if ext == ".pdf":
        return _convert_pdf_to_image(file_path)

    if ext in (".doc", ".docx"):
        return _convert_docx_to_image(file_path)

    return file_path, False


def _convert_pdf_to_image(file_path: str) -> Tuple[str, bool]:
    """Convert page 1 of PDF to a 300 DPI JPEG image."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF (fitz) not installed. Attempting fallback with pdf2image.")
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=300)
            if images:
                out_path = _get_converted_path(file_path)
                images[0].save(out_path, "JPEG", quality=95)
                logger.info(f"PDF converted to image via pdf2image: {out_path}")
                return out_path, True
        except Exception as e:
            raise RuntimeError(f"PDF conversion failed: {e}. Install PyMuPDF via: pip install PyMuPDF")
        raise RuntimeError("PDF conversion produced no output.")

    try:
        doc = fitz.open(file_path)
        page = doc[0]  # First page

        # Render at 300 DPI (300 / 72 = 4.1667x scale factor)
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)

        out_path = _get_converted_path(file_path)
        pix.save(out_path)

        doc.close()
        logger.info(f"PDF page rendered to high-res image: {out_path}")
        return out_path, True
    except Exception as e:
        logger.error(f"PyMuPDF conversion failed: {e}")
        return file_path, False


def _convert_docx_to_image(file_path: str) -> Tuple[str, bool]:
    """Convert DOCX embedded document image to JPEG."""
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("DOCX processing requires python-docx. Install via: pip install python-docx")

    try:
        doc = Document(file_path)
        # Extract embedded image inside document
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_data = rel.target_part.blob
                img = Image.open(io.BytesIO(image_data))
                img = img.convert("RGB")
                out_path = _get_converted_path(file_path)
                img.save(out_path, "JPEG", quality=95)
                logger.info(f"DOCX image extracted: {out_path}")
                return out_path, True

        return file_path, False
    except Exception as e:
        logger.error(f"DOCX conversion failed: {e}")
        return file_path, False


def _get_converted_path(original_path: str) -> str:
    """Generate target JPEG file path for converted image."""
    base = os.path.splitext(os.path.basename(original_path))[0]
    return str(UPLOAD_DIR / f"{base}_converted.jpg")

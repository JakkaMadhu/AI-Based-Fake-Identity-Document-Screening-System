"""
Document-to-Image Converter Service.
Converts PDF and DOCX files to images so the screening pipeline (OCR, ELA, ML)
can process them uniformly.
"""
import os
import io
import uuid
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
from ..utils.logging import logger

UPLOAD_DIR = Path("uploads")


def convert_document_to_image(file_path: str) -> Tuple[str, bool, Optional[str]]:
    """
    If the file at file_path is a PDF or DOCX, converts page 1 to a high-res JPG image
    and extracts its embedded native digital text layer if present.
    If it's an image, returns the original path unchanged.

    Returns: (image_file_path, was_converted, native_digital_text)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in (".jpg", ".jpeg", ".png"):
        return file_path, False, None

    if ext == ".pdf":
        return _convert_pdf_to_image(file_path)

    if ext in (".doc", ".docx"):
        return _convert_docx_to_image(file_path)

    return file_path, False, None


def _convert_pdf_to_image(file_path: str) -> Tuple[str, bool, Optional[str]]:
    """Convert the first page of a PDF to a high-res JPG and extract embedded vector text."""
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
                return out_path, True, None
        except ImportError:
            raise RuntimeError("PDF processing requires PyMuPDF. Install it with: pip install PyMuPDF")
        except Exception as e:
            raise RuntimeError(f"PDF conversion failed: {e}")
        raise RuntimeError("PDF conversion produced no output.")

    try:
        doc = fitz.open(file_path)
        page = doc[0]  # First page

        # Tier 1: Extract pure embedded digital vector text (100% ground truth)
        native_text = page.get_text()
        if native_text and len(native_text.strip()) > 20:
            logger.info(f"Extracted {len(native_text.strip())} characters of native digital text from PDF.")
        else:
            native_text = None

        # Render at 300 DPI for visual inspection and biometric cross-matching
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)

        out_path = _get_converted_path(file_path)
        pix.save(out_path)

        # Ensure valid JPEG
        if out_path.endswith(".jpg") and not _is_jpeg(out_path):
            img = Image.open(out_path)
            img = img.convert("RGB")
            img.save(out_path, "JPEG", quality=95)

        doc.close()
        logger.info(f"PDF page rendered to high-res image: {out_path}")
        return out_path, True, native_text
    except Exception as e:
        logger.error(f"PyMuPDF conversion failed: {e}")
        return file_path, False, None


def _convert_docx_to_image(file_path: str) -> Tuple[str, bool, Optional[str]]:
    """
    Convert DOCX to image and extract text.
    """
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("DOCX processing requires python-docx. Install it with: pip install python-docx")

    try:
        doc = Document(file_path)
        text_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        native_text = "\n".join(text_lines) if text_lines else None

        # Strategy 1: Extract embedded image
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_data = rel.target_part.blob
                img = Image.open(io.BytesIO(image_data))
                img = img.convert("RGB")
                out_path = _get_converted_path(file_path)
                img.save(out_path, "JPEG", quality=95)
                logger.info(f"DOCX image extracted and saved: {out_path}")
                return out_path, True, native_text

        # Strategy 2: Render text content as an image
        if text_lines:
            out_path = _get_converted_path(file_path)
            _render_text_to_image(text_lines, out_path)
            logger.info(f"DOCX text rendered as image: {out_path}")
            return out_path, True, native_text

        return file_path, False, None
    except Exception as e:
        logger.error(f"DOCX conversion failed: {e}")
        return file_path, False, None


def _render_text_to_image(text_lines: list, out_path: str):
    """Render text lines onto a white image for OCR processing."""
    # Calculate image dimensions based on text
    line_height = 32
    padding = 40
    max_chars = max(len(line) for line in text_lines) if text_lines else 40
    img_width = max(800, min(2400, max_chars * 16 + padding * 2))
    img_height = max(400, len(text_lines) * line_height + padding * 2)

    img = Image.new("RGB", (img_width, img_height), "white")

    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)

        # Try to use a decent font
        font = None
        for font_name in ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 20)
                break
            except (IOError, OSError):
                continue

        if font is None:
            font = ImageFont.load_default()

        y = padding
        for line in text_lines:
            draw.text((padding, y), line, fill="black", font=font)
            y += line_height
    except Exception as e:
        logger.warning(f"Text rendering with PIL failed: {e}")

    img.save(out_path, "JPEG", quality=95)


def _get_converted_path(original_path: str) -> str:
    """Generate a new file path for the converted image."""
    base = os.path.splitext(os.path.basename(original_path))[0]
    converted_name = f"{base}_converted.jpg"
    return str(UPLOAD_DIR / converted_name)


def _is_jpeg(file_path: str) -> bool:
    """Check if file starts with JPEG magic bytes."""
    try:
        with open(file_path, "rb") as f:
            return f.read(2) == b'\xff\xd8'
    except Exception:
        return False

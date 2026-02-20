from pathlib import Path


def extract_text(file_path: str) -> str:
    """Extract text from a PDF or image file."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_from_pdf(file_path)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        return _extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_from_pdf(file_path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF extraction. Run: pip install PyMuPDF")

    text_parts = []
    doc = fitz.open(file_path)
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts).strip()


def _extract_from_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError(
            "pytesseract and Pillow are required for image extraction. "
            "Run: pip install pytesseract Pillow  (and install tesseract-ocr system package)"
        )

    image = Image.open(file_path)
    return pytesseract.image_to_string(image).strip()

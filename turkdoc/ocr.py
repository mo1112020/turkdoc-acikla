"""OCR module for extracting Turkish text from images and PDFs."""

from pathlib import Path

import pytesseract
from PIL import Image, ImageEnhance, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MIN_TEXT_LENGTH = 20
MIN_IMAGE_WIDTH = 800


def _preprocess_image(image: Image.Image) -> Image.Image:
    """Convert to grayscale, increase contrast, and resize if too small."""
    gray = ImageOps.grayscale(image)
    enhanced = ImageEnhance.Contrast(gray).enhance(2.0)
    if enhanced.width < MIN_IMAGE_WIDTH:
        scale = MIN_IMAGE_WIDTH / enhanced.width
        new_size = (MIN_IMAGE_WIDTH, int(enhanced.height * scale))
        enhanced = enhanced.resize(new_size, Image.Resampling.LANCZOS)
    return enhanced


def _pdf_to_images(path: Path) -> list[Image.Image]:
    """Render PDF pages to PIL images using PyMuPDF."""
    import fitz

    images: list[Image.Image] = []
    doc = fitz.open(path)
    try:
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            images.append(img)
    finally:
        doc.close()
    return images


def _ocr_image(image: Image.Image) -> str:
    processed = _preprocess_image(image)
    return pytesseract.image_to_string(processed, lang="tur+eng")


def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image or PDF file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the format is unsupported or OCR yields too little text.
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_path}\n"
            "Please check the path and try again."
        )

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format: {suffix}\n"
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if suffix == ".pdf":
        images = _pdf_to_images(path)
        if not images:
            raise ValueError("The PDF file appears to be empty.")
        text_parts = [_ocr_image(img) for img in images]
        text = "\n".join(text_parts).strip()
    else:
        with Image.open(path) as img:
            text = _ocr_image(img).strip()

    if len(text) < MIN_TEXT_LENGTH:
        raise ValueError(
            "Could not extract enough text from the image.\n"
            "The image quality may be too low. Please retake the photo with:\n"
            "  • Better lighting (avoid shadows and glare)\n"
            "  • The document flat and fully visible\n"
            "  • Higher resolution / less blur"
        )

    return text

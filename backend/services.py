import json
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from backend.config import MAX_UPLOAD_SIZE_MB, UPLOAD_DIR
from backend.models import Document
from turkdoc.explainer import explain_document, is_likely_turkish
from turkdoc.ocr import SUPPORTED_EXTENSIONS, extract_text_from_image

ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS


def ensure_upload_dir(user_id: int) -> Path:
    path = UPLOAD_DIR / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(user_id: int, file: UploadFile) -> tuple[Path, str]:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    dest_dir = ensure_upload_dir(user_id)
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    dest_path = dest_dir / safe_name

    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    size = 0
    with dest_path.open("wb") as out:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                dest_path.unlink(missing_ok=True)
                raise ValueError(f"File too large. Maximum size is {MAX_UPLOAD_SIZE_MB} MB.")
            out.write(chunk)

    source_type = "pdf" if suffix == ".pdf" else "image"
    return dest_path, source_type


def extract_text(source_type: str, file_path: Path | None, text: str | None) -> str:
    if source_type == "text":
        if not text or len(text.strip()) < 10:
            raise ValueError("Text must be at least 10 characters.")
        return text.strip()

    if not file_path:
        raise ValueError("File path is required for image/pdf uploads.")

    return extract_text_from_image(str(file_path))


def apply_explanation(doc: Document, language: str) -> Document:
    if not is_likely_turkish(doc.extracted_text):
        pass  # still process; warning can be surfaced in API response later

    result = explain_document(doc.extracted_text, language)
    doc.language = language
    doc.document_type = result.get("document_type")
    doc.sent_by = result.get("sent_by")
    doc.explanation = result.get("explanation")
    doc.urgency = result.get("urgency")
    doc.reason = result.get("reason")
    doc.deadlines = result.get("deadlines")
    doc.next_steps = json.dumps(result.get("next_steps", []), ensure_ascii=False)
    doc.contacts = result.get("contacts")
    if not doc.title or doc.title == "Untitled Document":
        doc.title = result.get("document_type") or doc.title
    return doc


def delete_file(file_path: str | None) -> None:
    if file_path:
        Path(file_path).unlink(missing_ok=True)

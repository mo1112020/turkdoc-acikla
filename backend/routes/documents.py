import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.config import safe_error_message
from backend.database import get_db
from backend.models import Document, User
from backend.schemas import DocumentDetail, DocumentSummary, TextDocumentCreate
from backend.services import apply_explanation, delete_file, extract_text, save_upload

router = APIRouter(prefix="/api/documents", tags=["documents"])

DEFAULT_USER_ID = 1


def _ensure_default_user(db: Session) -> User:
    user = db.get(User, DEFAULT_USER_ID)
    if not user:
        user = User(
            id=DEFAULT_USER_ID,
            email="anonymous@local",
            name="Guest",
            hashed_password="-",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _to_detail(doc: Document) -> DocumentDetail:
    steps: list[str] = []
    if doc.next_steps:
        try:
            steps = json.loads(doc.next_steps)
        except json.JSONDecodeError:
            steps = []
    return DocumentDetail(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        original_filename=doc.original_filename,
        language=doc.language,
        document_type=doc.document_type,
        urgency=doc.urgency,
        created_at=doc.created_at,
        extracted_text=doc.extracted_text,
        sent_by=doc.sent_by,
        explanation=doc.explanation,
        reason=doc.reason,
        deadlines=doc.deadlines,
        next_steps=steps,
        contacts=doc.contacts,
    )


@router.get("", response_model=list[DocumentSummary])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return docs


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _to_detail(doc)


@router.post("/text", response_model=DocumentDetail, status_code=201)
def create_from_text(data: TextDocumentCreate, db: Session = Depends(get_db)):
    language = data.language.lower()
    if language not in ("english", "arabic"):
        raise HTTPException(status_code=400, detail="Language must be 'english' or 'arabic'")

    try:
        text = extract_text("text", None, data.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    user = _ensure_default_user(db)
    doc = Document(
        user_id=user.id,
        title=data.title,
        source_type="text",
        extracted_text=text,
        language=language,
    )
    db.add(doc)
    db.flush()

    try:
        apply_explanation(doc, language)
    except EnvironmentError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=safe_error_message(exc, fallback="AI service is not configured."),
        ) from exc
    except TimeoutError as exc:
        db.rollback()
        raise HTTPException(
            status_code=504,
            detail=safe_error_message(exc, fallback="The request timed out. Please try again."),
        ) from exc

    db.commit()
    db.refresh(doc)
    return _to_detail(doc)


@router.post("/upload", response_model=DocumentDetail, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(default="My Document"),
    language: str = Form(default="english"),
    db: Session = Depends(get_db),
):
    language = language.lower()
    if language not in ("english", "arabic"):
        raise HTTPException(status_code=400, detail="Language must be 'english' or 'arabic'")

    user = _ensure_default_user(db)

    try:
        file_path, source_type = save_upload(user.id, file)
        text = extract_text(source_type, file_path, None)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    doc = Document(
        user_id=user.id,
        title=title,
        source_type=source_type,
        original_filename=file.filename,
        file_path=str(file_path),
        extracted_text=text,
        language=language,
    )
    db.add(doc)
    db.flush()

    try:
        apply_explanation(doc, language)
    except EnvironmentError as exc:
        delete_file(str(file_path))
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=safe_error_message(exc, fallback="AI service is not configured."),
        ) from exc
    except TimeoutError as exc:
        delete_file(str(file_path))
        db.rollback()
        raise HTTPException(
            status_code=504,
            detail=safe_error_message(exc, fallback="The request timed out. Please try again."),
        ) from exc

    db.commit()
    db.refresh(doc)
    return _to_detail(doc)


@router.post("/{document_id}/explain", response_model=DocumentDetail)
def re_explain(
    document_id: int,
    language: str = Query(default="english"),
    db: Session = Depends(get_db),
):
    language = language.lower()
    if language not in ("english", "arabic"):
        raise HTTPException(status_code=400, detail="Language must be 'english' or 'arabic'")

    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        apply_explanation(doc, language)
    except EnvironmentError as exc:
        raise HTTPException(
            status_code=500,
            detail=safe_error_message(exc, fallback="AI service is not configured."),
        ) from exc
    except TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=safe_error_message(exc, fallback="The request timed out. Please try again."),
        ) from exc

    db.commit()
    db.refresh(doc)
    return _to_detail(doc)


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_file(doc.file_path)
    db.delete(doc)
    db.commit()

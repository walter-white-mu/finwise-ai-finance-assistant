from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.document import Document, DocumentChunk
from app.schemas.document import DocumentAnswer, DocumentQuestion, DocumentResponse
from app.services import document_service

router = APIRouter(prefix="/api/documents", tags=["Document Intelligence"])


def to_response(db: Session, doc: Document) -> dict:
    return {"id": doc.id, "filename": doc.filename, "size_bytes": doc.size_bytes, "status": doc.status,
            "error_message": doc.error_message, "page_count": doc.page_count,
            "chunk_count": db.query(DocumentChunk).filter_by(document_id=doc.id).count(), "created_at": doc.created_at}


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported.")
    content = await file.read(document_service.MAX_UPLOAD_BYTES + 1)
    if len(content) > document_service.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"PDF exceeds the {document_service.MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="The uploaded file is not a valid PDF.")
    document_id = str(uuid4())
    storage_key = f"{uuid4().hex}.pdf"
    document_service.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = document_service.STORAGE_DIR / storage_key
    path.write_bytes(content)
    doc = Document(id=document_id, filename=Path(file.filename or "document.pdf").name[:255], storage_key=storage_key,
                   size_bytes=len(content), status="PENDING")
    db.add(doc)
    try:
        db.commit()
        db.refresh(doc)
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return to_response(db, doc)


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return [to_response(db, doc) for doc in db.query(Document).order_by(Document.created_at.desc()).all()]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return to_response(db, doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    path = document_service.STORAGE_DIR / doc.storage_key
    db.delete(doc)
    db.commit()
    path.unlink(missing_ok=True)


@router.post("/{document_id}/process", response_model=DocumentResponse)
async def process_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        doc = await document_service.process_document(db, doc)
    except document_service.OllamaUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return to_response(db, doc)


@router.post("/ask", response_model=DocumentAnswer)
async def ask_documents(data: DocumentQuestion, db: Session = Depends(get_db)):
    try:
        return await document_service.ask_documents(db, data.question)
    except document_service.OllamaUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

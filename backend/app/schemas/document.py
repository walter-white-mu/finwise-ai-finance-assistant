from datetime import datetime
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    filename: str
    size_bytes: int
    status: str
    error_message: str | None = None
    page_count: int | None = None
    chunk_count: int = 0
    created_at: datetime


class DocumentQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class DocumentSource(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    excerpt: str
    similarity: float


class DocumentAnswer(BaseModel):
    answer: str
    sources: list[DocumentSource]

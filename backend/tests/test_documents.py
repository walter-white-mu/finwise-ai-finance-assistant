import asyncio

import pymupdf
import pytest

from app.services import document_service
from app.services.document_service import DocumentProcessingError, chunk_pages, embed_text, extract_pdf_pages


def test_chunk_pages_preserves_page_and_splits_long_text():
    chunks = chunk_pages([(3, "word " * 700)])
    assert len(chunks) > 1
    assert all(page == 3 for page, _, _ in chunks)
    assert chunks[0][1] == 0
    assert all(text.strip() for _, _, text in chunks)


def test_extract_pdf_pages_keeps_one_based_page_numbers(tmp_path):
    path = tmp_path / "statement.pdf"
    pdf = pymupdf.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Account statement balance $125.00")
    pdf.save(path)
    pdf.close()

    assert extract_pdf_pages(path)[0][0] == 1
    assert "125.00" in extract_pdf_pages(path)[0][1]


def test_scanned_pdf_reports_ocr_not_implemented(tmp_path):
    path = tmp_path / "scanned.pdf"
    pdf = pymupdf.open()
    pdf.new_page()
    pdf.save(path)
    pdf.close()

    with pytest.raises(DocumentProcessingError, match="OCR support is not implemented"):
        extract_pdf_pages(path)


def test_corrupted_pdf_is_reported(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"%PDF-1.7 not a real PDF")

    with pytest.raises(DocumentProcessingError, match="corrupted"):
        extract_pdf_pages(path)


def test_embedding_generation_uses_ollama_embedding_response(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"embeddings": [[0.25, -0.5, 0.75]]}

    class Client:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, *_args, **_kwargs):
            return Response()

    monkeypatch.setattr(document_service.httpx, "AsyncClient", Client)
    assert asyncio.run(embed_text("monthly account balance")) == [0.25, -0.5, 0.75]

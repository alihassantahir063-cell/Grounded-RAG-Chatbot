from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.services.document import extract_documents_from_upload


def test_text_upload_is_chunked_with_source_metadata():
    chunks = extract_documents_from_upload("notes.txt", b"Project deadline: Friday.")

    assert len(chunks) == 1
    assert chunks[0].page_content == "Project deadline: Friday."
    assert chunks[0].metadata["source"] == "notes.txt"
    assert chunks[0].metadata["page"] == 1
    assert chunks[0].metadata["chunk_index"] == 0


def test_blank_pdf_has_no_extractable_documents():
    pdf_bytes = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(pdf_bytes)

    assert extract_documents_from_upload("blank.pdf", pdf_bytes.getvalue()) == []


def test_corrupt_pdf_returns_a_validation_error():
    with pytest.raises(ValueError, match="invalid or corrupted"):
        extract_documents_from_upload("corrupt.pdf", b"not a PDF")

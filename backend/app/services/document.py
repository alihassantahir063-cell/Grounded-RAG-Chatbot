from __future__ import annotations

from io import BytesIO
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.config import settings


def extract_text_from_pdf_bytes(file_bytes: bytes, file_name: str) -> List[Document]:
    try:
        reader = PdfReader(BytesIO(file_bytes))
    except (PdfReadError, ValueError) as exc:
        raise ValueError("The PDF is invalid or corrupted.") from exc

    documents: List[Document] = []
    try:
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": file_name,
                            "page": page_number,
                        },
                    )
                )
    except (PdfReadError, ValueError) as exc:
        raise ValueError("The PDF could not be read.") from exc
    return documents


def extract_text_from_txt_bytes(file_bytes: bytes, file_name: str) -> List[Document]:
    text = file_bytes.decode("utf-8", errors="ignore")
    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={
                "source": file_name,
                "page": 1,
            },
        )
    ]


def chunk_documents(documents: List[Document]) -> List[Document]:
    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index
    return chunks


def extract_documents_from_upload(file_name: str, file_bytes: bytes) -> List[Document]:
    lower_name = file_name.lower()
    if lower_name.endswith(".pdf"):
        extracted = extract_text_from_pdf_bytes(file_bytes, file_name)
    elif lower_name.endswith(".txt"):
        extracted = extract_text_from_txt_bytes(file_bytes, file_name)
    else:
        raise ValueError("Unsupported file type. Upload a PDF or TXT file.")

    return chunk_documents(extracted)

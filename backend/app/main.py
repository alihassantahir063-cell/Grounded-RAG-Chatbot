from __future__ import annotations

from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, RateLimitError
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.schemas import ChatResponse, QuestionRequest, SourceItem, UploadFileResponse
from app.services.document import extract_documents_from_upload
from app.services.rag import RAGService

app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()


def get_max_upload_size_bytes() -> int:
    return max(int(settings.MAX_UPLOAD_SIZE_MB), 1) * 1024 * 1024


def require_openai_api_key() -> None:
    api_key = (settings.OPENAI_API_KEY or "").strip()
    if not api_key or api_key.lower() in {"your_api_key_here", "your-openai-api-key"}:
        raise HTTPException(
            status_code=503,
            detail="OpenAI is not configured. Set a valid OPENAI_API_KEY in backend/.env.",
        )


def openai_http_exception(exc: APIError) -> HTTPException:
    if isinstance(exc, AuthenticationError):
        return HTTPException(
            status_code=503,
            detail="The configured API key was rejected. Check OPENAI_API_KEY or OPENROUTER_API_KEY in backend/.env.",
        )
    if isinstance(exc, RateLimitError):
        return HTTPException(
            status_code=503,
            detail="OpenAI rate limit or quota reached. Check your account and try again later.",
        )
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return HTTPException(
            status_code=502,
            detail="Could not connect to OpenAI. Check your network and try again.",
        )
    return HTTPException(status_code=502, detail="The OpenAI request failed.")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadFileResponse)
async def upload_document(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")
    if len(files) > settings.MAX_UPLOAD_FILES:
        raise HTTPException(
            status_code=413,
            detail=f"Upload at most {settings.MAX_UPLOAD_FILES} files at a time.",
        )

    max_upload_size_bytes = get_max_upload_size_bytes()
    require_openai_api_key()
    documents = []
    uploaded_file_names = []

    for uploaded_file in files:
        if not uploaded_file.filename:
            continue

        try:
            file_bytes = await uploaded_file.read(max_upload_size_bytes + 1)
            if len(file_bytes) > max_upload_size_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"{uploaded_file.filename} exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB upload limit.",
                )
            chunks = await run_in_threadpool(
                extract_documents_from_upload,
                uploaded_file.filename,
                file_bytes,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            await uploaded_file.close()

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail=f"No readable content found in {uploaded_file.filename}.",
            )

        documents.extend(chunks)
        uploaded_file_names.append(uploaded_file.filename)

    if not documents:
        raise HTTPException(status_code=400, detail="No valid document content was extracted.")

    try:
        await run_in_threadpool(rag_service.build_vectorstore, documents)
    except APIError as exc:
        raise openai_http_exception(exc) from exc

    return UploadFileResponse(
        message="Document uploaded and indexed successfully.",
        files=uploaded_file_names,
        document_count=len(documents),
    )


@app.post("/ask", response_model=ChatResponse)
async def ask_question(payload: QuestionRequest):
    if not rag_service.vectorstore:
        raise HTTPException(status_code=400, detail="Upload a document before asking a question.")
    require_openai_api_key()

    try:
        result = await run_in_threadpool(rag_service.answer_question, payload.question)
    except APIError as exc:
        raise openai_http_exception(exc) from exc
    answer = result["answer"]
    sources = result["sources"]

    response_sources = [
        SourceItem(
            file_name=item["file_name"],
            page_number=item.get("page_number"),
            chunk_index=item.get("chunk_index"),
            content=item["content"],
        )
        for item in sources
    ]

    return ChatResponse(answer=answer, sources=response_sources)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

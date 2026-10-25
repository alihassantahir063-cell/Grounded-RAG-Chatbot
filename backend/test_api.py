from fastapi.testclient import TestClient

from app import main


class FakeRAGService:
    def __init__(self):
        self.vectorstore = None

    def build_vectorstore(self, documents):
        self.vectorstore = object()

    def answer_question(self, question):
        return {"answer": "Friday.", "sources": []}


def test_upload_reports_missing_openai_configuration(monkeypatch):
    monkeypatch.setattr(main.settings, "OPENAI_API_KEY", "your_api_key_here")

    response = TestClient(main.app).post(
        "/upload",
        files=[("files", ("notes.txt", b"Project deadline: Friday.", "text/plain"))],
    )

    assert response.status_code == 503
    assert response.json()["detail"].startswith("OpenAI is not configured.")


def test_upload_and_question_use_document_service(monkeypatch):
    fake_rag_service = FakeRAGService()
    monkeypatch.setattr(main, "rag_service", fake_rag_service)
    monkeypatch.setattr(main.settings, "OPENAI_API_KEY", "test-key")
    client = TestClient(main.app)

    upload_response = client.post(
        "/upload",
        files=[("files", ("notes.txt", b"Project deadline: Friday.", "text/plain"))],
    )
    ask_response = client.post("/ask", json={"question": "When is the deadline?"})

    assert upload_response.status_code == 200
    assert upload_response.json()["files"] == ["notes.txt"]
    assert upload_response.json()["document_count"] == 1
    assert ask_response.status_code == 200
    assert ask_response.json()["answer"] == "Friday."


def test_upload_returns_bad_request_for_corrupt_pdf(monkeypatch):
    monkeypatch.setattr(main.settings, "OPENAI_API_KEY", "test-key")

    response = TestClient(main.app).post(
        "/upload",
        files=[("files", ("corrupt.pdf", b"not a PDF", "application/pdf"))],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The PDF is invalid or corrupted."

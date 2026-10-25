from langchain_core.documents import Document

from app.services import rag as rag_module
from app.services.rag import RAGService


class EmptyRetriever:
    def invoke(self, question: str) -> list:
        return []


def test_empty_retrieval_returns_exact_refusal():
    service = object.__new__(RAGService)
    service.vectorstore = object()
    service.retriever = EmptyRetriever()

    result = service.answer_question("What is the document about?")

    assert result == {
        "answer": "I cannot find this information in the uploaded document.",
        "sources": [],
    }


def test_reindexing_replaces_old_chunks(monkeypatch):
    class FakeVectorStore:
        collections = {}

        def __init__(self, collection_name, **kwargs):
            self.collection = self.collections.setdefault(collection_name, {})

        def get(self, include):
            return {"ids": list(self.collection)}

        def add_documents(self, documents):
            ids = [f"chunk-{len(self.collection) + index}" for index in range(len(documents))]
            self.collection.update(zip(ids, documents))
            return ids

        def delete(self, ids):
            for document_id in ids:
                self.collection.pop(document_id, None)

        def persist(self):
            pass

        def as_retriever(self, **kwargs):
            return object()

    FakeVectorStore.collections = {}
    monkeypatch.setattr(rag_module, "Chroma", FakeVectorStore)
    service = object.__new__(RAGService)
    service.embeddings = object()
    service.vectorstore = None
    service.retriever = None

    service.build_vectorstore([Document(page_content="Old document")])
    service.build_vectorstore([Document(page_content="New document")])

    indexed_documents = list(FakeVectorStore.collections["document_chunks"].values())
    assert [document.page_content for document in indexed_documents] == ["New document"]

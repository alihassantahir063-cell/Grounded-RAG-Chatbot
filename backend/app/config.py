import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    return value


OPENROUTER_API_KEY = get_setting("OPENROUTER_API_KEY")
OPENAI_API_KEY = get_setting("OPENAI_API_KEY") or OPENROUTER_API_KEY
OPENROUTER_BASE_URL = get_setting("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


class Settings:
    APP_TITLE = "Document RAG Chatbot"
    APP_VERSION = "1.0.0"
    OPENAI_API_KEY = OPENAI_API_KEY
    OPENROUTER_API_KEY = OPENROUTER_API_KEY
    OPENROUTER_BASE_URL = OPENROUTER_BASE_URL
    OPENAI_MODEL = get_setting(
        "OPENAI_MODEL",
        "openai/gpt-4o-mini" if OPENROUTER_API_KEY else "gpt-4o-mini",
    )
    EMBEDDING_MODEL = get_setting(
        "EMBEDDING_MODEL",
        "openai/text-embedding-3-small" if OPENROUTER_API_KEY else "text-embedding-3-small",
    )
    CHUNK_SIZE = int(get_setting("CHUNK_SIZE", "1200"))
    CHUNK_OVERLAP = int(get_setting("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(get_setting("TOP_K_RESULTS", "4"))
    VECTOR_DB_PATH = get_setting("VECTOR_DB_PATH", str(BASE_DIR / "storage" / "chroma"))
    MAX_UPLOAD_SIZE_MB = int(get_setting("MAX_UPLOAD_SIZE_MB", "20"))
    MAX_UPLOAD_FILES = int(get_setting("MAX_UPLOAD_FILES", "10"))
    CORS_ORIGINS = [
        origin.strip()
        for origin in get_setting(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    def __init__(self):
        if self.CHUNK_SIZE <= 0:
            raise ValueError("CHUNK_SIZE must be greater than zero.")
        if not 0 <= self.CHUNK_OVERLAP < self.CHUNK_SIZE:
            raise ValueError("CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE.")
        if self.TOP_K_RESULTS <= 0:
            raise ValueError("TOP_K_RESULTS must be greater than zero.")
        if self.MAX_UPLOAD_SIZE_MB <= 0 or self.MAX_UPLOAD_FILES <= 0:
            raise ValueError("Upload size and file-count limits must be greater than zero.")


settings = Settings()

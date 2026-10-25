from typing import List, Optional

from pydantic import BaseModel, Field


class UploadFileResponse(BaseModel):
    message: str
    files: List[str]
    document_count: int


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)


class SourceItem(BaseModel):
    file_name: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []

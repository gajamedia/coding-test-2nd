from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    question: str = Field(..., example="Apa isi laporan laba rugi tahun 2023?")
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class DocumentSource(BaseModel):
    content: str
    page: int
    score: float
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str
    sources: List[DocumentSource]
    processing_time: float  # in seconds


class DocumentInfo(BaseModel):
    filename: str
    upload_date: datetime
    chunks_count: int
    status: str  # e.g. "processed", "pending", "failed"


class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]


class UploadResponse(BaseModel):
    message: str = Field(..., example="Upload and processing successful")
    filename: str
    chunks_count: int
    processing_time: float  # in seconds


class ChunkInfo(BaseModel):
    id: str
    content: str
    page: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChunksResponse(BaseModel):
    chunks: List[ChunkInfo]
    total_count: int

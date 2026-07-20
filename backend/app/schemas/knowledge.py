from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KBCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    department: str = Field(default="", max_length=100)
    color: str = Field(default="linear-gradient(135deg,#4a8cf7,#00d4ff)")


class KBUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    department: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)


class KBInfo(BaseModel):
    id: int
    name: str
    description: str
    department: str
    color: str
    doc_count: int = 0
    chunk_count: int = 0
    total_size: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentInfo(BaseModel):
    id: int
    kb_id: int
    filename: str
    original_name: str
    file_type: str
    file_size: int
    status: str
    error_msg: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    query: str = Field(..., description="检索问题")
    kb_ids: Optional[list[int]] = Field(None, description="指定知识库ID列表，为空则检索全部")
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    answer: str
    sources: list["SourceInfo"]
    latency_ms: int
    tokens_used: int


class SourceInfo(BaseModel):
    doc_id: int
    doc_name: str
    chunk_index: int
    content: str
    score: float
    page: Optional[str] = None


class DashboardStats(BaseModel):
    kb_count: int
    doc_count: int
    query_count_today: int
    storage_bytes: int

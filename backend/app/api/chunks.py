"""分块查询接口"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.knowledge_base import DocumentChunk, Document

router = APIRouter()


@router.get("/chunks/{chunk_id}")
async def get_chunk(
    chunk_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个分块内容"""
    result = await db.execute(select(DocumentChunk).where(DocumentChunk.id == chunk_id))
    chunk = result.scalar_one_or_none()
    if not chunk:
        raise HTTPException(status_code=404, detail="分块不存在")

    # 获取文档名
    doc_result = await db.execute(select(Document).where(Document.id == chunk.doc_id))
    doc = doc_result.scalar_one_or_none()

    return {
        "id": chunk.id,
        "doc_id": chunk.doc_id,
        "doc_name": doc.original_name if doc else "未知",
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
        "kb_id": chunk.kb_id,
    }

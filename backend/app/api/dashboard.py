from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.knowledge_base import KnowledgeBase, Document
from ..schemas.knowledge import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb_count = await db.scalar(select(func.count(KnowledgeBase.id)))
    doc_count = await db.scalar(select(func.count(Document.id)))
    storage = await db.scalar(
        select(func.coalesce(func.sum(Document.file_size), 0))
    )

    return DashboardStats(
        kb_count=kb_count or 0,
        doc_count=doc_count or 0,
        query_count_today=0,  # 在生产环境从查询日志统计
        storage_bytes=storage or 0,
    )

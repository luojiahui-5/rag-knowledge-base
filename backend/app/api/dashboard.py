from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.knowledge_base import KnowledgeBase, Document, QueryLog
from ..schemas.knowledge import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb_count = await db.scalar(select(func.count(KnowledgeBase.id)))
    doc_count = await db.scalar(select(func.count(Document.id)))
    storage = await db.scalar(select(func.coalesce(func.sum(Document.file_size), 0)))

    # 今日查询次数
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    query_count_today = await db.scalar(
        select(func.count(QueryLog.id)).where(QueryLog.created_at >= today)
    )

    return DashboardStats(
        kb_count=kb_count or 0,
        doc_count=doc_count or 0,
        query_count_today=query_count_today or 0,
        storage_bytes=storage or 0,
    )


@router.get("/trend")
async def get_trend(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询趋势数据：最近 N 天每天的查询次数"""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = []
    for i in range(days - 1, -1, -1):
        day_start = today - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = await db.scalar(
            select(func.count(QueryLog.id)).where(
                QueryLog.created_at >= day_start,
                QueryLog.created_at < day_end,
            )
        )
        result.append({
            "date": day_start.strftime("%m-%d"),
            "label": ["周一","周二","周三","周四","周五","周六","周日"][day_start.weekday()],
            "count": count or 0,
        })
    return result

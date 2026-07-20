from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.knowledge_base import KnowledgeBase, Document, DocumentChunk, kb_members
from ..schemas.knowledge import KBCreate, KBUpdate, KBInfo

router = APIRouter()


@router.get("", response_model=list[KBInfo])
async def list_knowledge_bases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户可访问的知识库列表"""
    import traceback
    try:
        return await _list_kbs(db, current_user)
    except Exception as e:
        traceback.print_exc()
        raise

async def _list_kbs(db, current_user):
    if current_user.role == "admin":
        result = await db.execute(select(KnowledgeBase).order_by(KnowledgeBase.updated_at.desc()))
        kbs = result.scalars().all()
    else:
        # 非管理员只返回有权限的知识库
        result = await db.execute(
            select(KnowledgeBase)
            .join(kb_members, KnowledgeBase.id == kb_members.c.kb_id, isouter=True)
            .where(
                (KnowledgeBase.created_by == current_user.id) |
                (kb_members.c.user_id == current_user.id)
            )
            .order_by(KnowledgeBase.updated_at.desc())
        )
        kbs = result.unique().scalars().all()

    return [await _enrich_kb_info(kb, db) for kb in kbs]


@router.post("", response_model=KBInfo, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    req: KBCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kb = KnowledgeBase(
        name=req.name,
        description=req.description,
        department=req.department or current_user.department,
        color=req.color,
        created_by=current_user.id,
    )
    db.add(kb)
    await db.flush()
    await db.refresh(kb)
    return await _enrich_kb_info(kb, db)


@router.get("/{kb_id}", response_model=KBInfo)
async def get_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return await _enrich_kb_info(kb, db)


@router.put("/{kb_id}", response_model=KBInfo)
async def update_knowledge_base(
    kb_id: int,
    req: KBUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kb, key, value)

    await db.flush()
    await db.refresh(kb)
    return await _enrich_kb_info(kb, db)


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    if current_user.role != "admin" and kb.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此知识库")

    await db.delete(kb)
    await db.flush()


async def _enrich_kb_info(kb: KnowledgeBase, db: AsyncSession) -> KBInfo:
    """填充文档数、切片数、存储大小等统计信息"""
    doc_count_result = await db.execute(
        select(func.count(Document.id)).where(Document.kb_id == kb.id)
    )
    doc_count = doc_count_result.scalar() or 0

    chunk_count_result = await db.execute(
        select(func.count(DocumentChunk.id)).where(DocumentChunk.kb_id == kb.id)
    )
    chunk_count = chunk_count_result.scalar() or 0

    size_result = await db.execute(
        select(func.coalesce(func.sum(Document.file_size), 0)).where(Document.kb_id == kb.id)
    )
    total_size = size_result.scalar() or 0

    return KBInfo(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        department=kb.department,
        color=kb.color,
        doc_count=doc_count,
        chunk_count=chunk_count,
        total_size=total_size,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )

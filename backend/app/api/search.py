import time
import numpy as np
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import get_settings
from ..models.user import User
from ..models.knowledge_base import DocumentChunk, Document
from ..schemas.knowledge import SearchRequest, SearchResult, SourceInfo
from ..services.llm_service import generate_answer
from ..services.embedding_service import embed_text, cosine_similarity

router = APIRouter()
settings = get_settings()


@router.post("", response_model=SearchResult)
async def search(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t0 = time.time()
    print(f"\n[Search] query='{req.query}', kb_ids={req.kb_ids}")

    # ========== 1. 构建查询条件 ==========
    conditions = []
    if req.kb_ids:
        conditions.append(DocumentChunk.kb_id.in_(req.kb_ids))

    # ========== 2. 关键词检索（多关键词 LIKE 匹配） ==========
    keyword_sql = select(DocumentChunk)
    if req.query:
        from sqlalchemy import or_
        # 中文：将整个查询作为 LIKE 模式 + 提取所有 2-gram 子串做 OR 匹配
        like_filters = [DocumentChunk.content.like(f"%{req.query}%")]
        if len(req.query) >= 3:
            for i in range(len(req.query) - 1):
                sub = req.query[i:i+2]
                if len(sub) >= 2:
                    like_filters.append(DocumentChunk.content.like(f"%{sub}%"))
        keyword_sql = keyword_sql.where(or_(*like_filters[:10]))
    if conditions:
        keyword_sql = keyword_sql.where(*conditions)
    keyword_sql = keyword_sql.limit(settings.KEYWORD_TOP_K)
    keyword_result = await db.execute(keyword_sql)
    keyword_chunks = keyword_result.scalars().all()
    print(f"[Search] keyword_chunks: {len(keyword_chunks)}")

    # ========== 3. 向量语义检索（可选，模型未安装时回退到关键词） ==========
    vector_chunks = []
    try:
        query_vec = embed_text(req.query)
        all_sql = select(DocumentChunk)
        if conditions:
            all_sql = all_sql.where(*conditions)
        all_result = await db.execute(all_sql)
        all_chunks = all_result.scalars().all()

        scored = []
        for chunk in all_chunks:
            if not hasattr(chunk, '_cached_vec'):
                break
            sim = cosine_similarity(query_vec, chunk._cached_vec)
            scored.append((chunk, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        vector_chunks = [c for c, _ in scored[:settings.VECTOR_TOP_K]]
    except Exception:
        vector_chunks = keyword_chunks[:settings.VECTOR_TOP_K] if keyword_chunks else []

    # 合并结果
    if not vector_chunks:
        vector_chunks = keyword_chunks[:settings.VECTOR_TOP_K]
    if not keyword_chunks:
        keyword_chunks = vector_chunks[:settings.KEYWORD_TOP_K]

    # ========== 4. RRF 融合 ==========
    alpha = settings.SEMANTIC_WEIGHT
    rrf_scores = {}
    for rank, chunk in enumerate(keyword_chunks):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + (1 - alpha) / (rank + 60)
    for rank, chunk in enumerate(vector_chunks):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + alpha / (rank + 60)

    sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:settings.RERANKER_TOP_K]

    # ========== 5. 获取 chunk 详情 + 组装上下文 ==========
    if sorted_ids:
        detail_result = await db.execute(
            select(DocumentChunk).where(DocumentChunk.id.in_(sorted_ids))
        )
        top_chunks = {c.id: c for c in detail_result.scalars().all()}
    else:
        top_chunks = {}

    context_parts = []
    sources = []
    for cid in sorted_ids:
        chunk = top_chunks.get(cid)
        if not chunk:
            continue
        # 获取文档名
        doc_result = await db.execute(select(Document).where(Document.id == chunk.doc_id))
        doc = doc_result.scalar_one_or_none()
        doc_name = doc.original_name if doc else "未知文档"

        context_parts.append(chunk.content)
        raw_content = chunk.content or ""
        sources.append({
            "chunk_id": chunk.id,
            "doc_id": chunk.doc_id,
            "doc_name": doc_name,
            "chunk_index": chunk.chunk_index,
            "content": raw_content,
            "page": f"分块 {chunk.chunk_index}",
            "score": round(rrf_scores.get(cid, 0), 4),
        })

    print(f"[Search DEBUG] sources count={len(sources)}, first content len={len(sources[0]['content']) if sources else 0}", flush=True)

    # ========== 6. DeepSeek LLM 生成 ==========
    print(f"[Search] sources after assembly: {len(sources)}, context length: {sum(len(c) for c in context_parts)}")
    context = "\n\n---\n\n".join(context_parts)
    answer = await generate_answer(req.query, context, sources)

    latency = int((time.time() - t0) * 1000)
    return SearchResult(
        answer=answer,
        sources=[SourceInfo(
            doc_id=s.get("doc_id", s["chunk_index"]),
            doc_name=s["doc_name"],
            chunk_index=s["chunk_index"],
            content=s.get("content", ""),
            score=s["score"],
            page=s.get("page", f"分块 {s['chunk_index']}"),
        ) for s in sources],
        latency_ms=latency,
        tokens_used=len(context) // 2,
    )

"""Debug search endpoint - tests the search logic directly"""
import time, re
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.knowledge_base import DocumentChunk, Document

router = APIRouter()


def extract_kw(text):
    puncts = '？！，。、；：（）【】"\' \t\n\r'
    cleaned = re.sub('[' + puncts + ']+', ' ', text).strip()
    parts = re.split(r'([a-zA-Z]+)', cleaned)
    keywords = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if re.match(r'^[a-zA-Z]+$', part):
            if len(part) >= 2:
                keywords.append(part)
                keywords.append(part.lower())
        else:
            for n in [3, 2]:
                for i in range(len(part) - n + 1):
                    kw = part[i:i+n]
                    if len(kw) >= 2:
                        keywords.append(kw)
    seen = set()
    result = []
    for kw in keywords:
        if kw not in seen and len(kw) >= 2:
            seen.add(kw)
            result.append(kw)
    return result[:15]


@router.post("/debug-search")
async def debug_search(
    query: str = "Redis集群",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t0 = time.time()

    # Step 1: Extract keywords
    keywords = extract_kw(query)

    # Step 2: Search
    like_filters = [DocumentChunk.content.like(f"%{kw}%") for kw in keywords]
    result = await db.execute(
        select(DocumentChunk).where(or_(*like_filters[:10])).limit(50)
    )
    chunks = result.scalars().all()

    # Step 3: Get doc names
    sources = []
    for c in chunks[:5]:
        d = await db.execute(select(Document).where(Document.id == c.doc_id))
        doc = d.scalar_one_or_none()
        sources.append({
            "chunk_id": c.id,
            "doc_name": doc.original_name if doc else "?",
            "content_preview": c.content[:100],
        })

    # Step 4: Try DeepSeek
    context = "\n\n---\n\n".join([c.content for c in chunks[:3]])
    try:
        import httpx
        resp = httpx.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": "Bearer sk-8b35bd845c8f4c1c9cd561a51c48ce8e"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "根据资料回答问题。仅用资料中的信息。"},
                    {"role": "user", "content": f"资料：\n{context}\n\n问题：{query}"},
                ],
                "max_tokens": 500,
            },
            timeout=60,
        )
        answer = resp.json()["choices"][0]["message"]["content"] if resp.status_code == 200 else f"HTTP {resp.status_code}"
    except Exception as e:
        answer = f"LLM Error: {e}"

    return {
        "query": query,
        "keywords": keywords,
        "chunks_found": len(chunks),
        "sources": sources,
        "answer": answer,
        "latency_ms": (time.time() - t0) * 1000,
    }

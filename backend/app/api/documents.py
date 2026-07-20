import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..core.database import get_db
from ..core.security import get_current_user
from ..core.config import get_settings
from ..models.user import User
from ..models.knowledge_base import KnowledgeBase, Document, DocumentChunk
from ..schemas.knowledge import DocumentInfo

router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "pptx", "ppt", "xlsx", "xls", "md", "txt", "html", "htm"}


@router.get("", response_model=list[DocumentInfo])
async def list_documents(
    kb_id: int = None,
    status: str = None,
    file_type: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Document)
    if kb_id:
        query = query.where(Document.kb_id == kb_id)
    if status:
        query = query.where(Document.status == status)
    if file_type:
        query = query.where(Document.file_type == file_type)
    query = query.order_by(Document.created_at.desc()).limit(100)

    result = await db.execute(query)
    docs = result.scalars().all()
    return [DocumentInfo.model_validate(d) for d in docs]


@router.post("/upload", response_model=DocumentInfo, status_code=status.HTTP_201_CREATED)
async def upload_document(
    kb_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 校验知识库
    kb_result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = kb_result.scalar_one_or_none()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 校验文件类型
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: .{ext}")

    # 保存文件
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        kb_id=kb_id,
        filename=unique_name,
        original_name=file.filename,
        file_type=ext,
        file_size=len(content),
        file_path=file_path,
        status="uploading",
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    # 同步处理文档（解析 + 切片 + 入库）
    import json

    try:
        doc.status = "parsing"
        await db.flush()

        # 尝试解析文档（依赖 PyMuPDF/python-docx，未安装时按纯文本处理）
        try:
            from ..services.document_processor import parse_file, chunk_text
            text = parse_file(file_path, ext)
        except (ImportError, Exception):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if not text or (text.startswith("[") and "失败" in text):
            raise ValueError(text or "解析结果为空")

        doc.status = "chunking"
        await db.flush()

        # 简易切片
        try:
            from ..services.document_processor import chunk_text
            chunks = chunk_text(text)
        except ImportError:
            chunks = [{"content": text[i:i+512], "metadata": {}} for i in range(0, len(text), 480) if text[i:i+512].strip()]

        for idx, ch in enumerate(chunks):
            chunk = DocumentChunk(
                doc_id=doc.id,
                kb_id=kb_id,
                chunk_index=idx,
                content=ch["content"],
                metadata_json=json.dumps(ch.get("metadata", {}), ensure_ascii=False),
            )
            db.add(chunk)

        doc.chunk_count = len(chunks)
        doc.status = "done"
    except Exception as e:
        doc.status = "failed"
        doc.error_msg = str(e)[:500]

    await db.flush()
    await db.refresh(doc)
    return DocumentInfo.model_validate(doc)


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return DocumentInfo.model_validate(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 删除物理文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    await db.flush()


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="文件已被清理")

    return FileResponse(doc.file_path, filename=doc.original_name)


@router.get("/{doc_id}/preview")
async def preview_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """将任意文档解析为纯文本预览"""
    from ..services.document_processor import parse_file

    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="文件已被清理")

    try:
        text = parse_file(doc.file_path, doc.file_type)
        return {
            "doc_id": doc.id,
            "filename": doc.original_name,
            "file_type": doc.file_type,
            "content": text,
            "content_length": len(text),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)}")

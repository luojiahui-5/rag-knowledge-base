from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .core.database import engine, Base
from .api import auth, knowledge, documents, search, dashboard

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建表（生产环境请用 Alembic 迁移）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS（生产环境应限制 origin）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["仪表盘"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["文档"])
app.include_router(search.router, prefix="/api/v1/search", tags=["检索"])

# 分块查询
from .api import chunks
app.include_router(chunks.router, prefix="/api/v1", tags=["分块"])

# 调试端点
from .api import debug_search
app.include_router(debug_search.router, prefix="/api/v1", tags=["调试"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


# 生产环境：托管前端静态文件（Render 一键部署用）
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "dist")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    if not os.path.exists(FRONTEND_DIR):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not built. Run: npm run build")
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

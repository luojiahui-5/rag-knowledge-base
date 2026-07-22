from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "智能知识库系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "rag_knowledge_base"
    DATABASE_URL: str = ""

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # Elasticsearch
    ES_HOST: str = "http://localhost:9200"

    # LLM - DeepSeek
    DEEPSEEK_API_KEY: str = "sk-8b35bd845c8f4c1c9cd561a51c48ce8e"
    LLM_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    LLM_MODEL: str = "deepseek-chat"
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.3

    # Embedding（本地 BGE 模型）
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 1024

    # Retrieval
    VECTOR_TOP_K: int = 50
    KEYWORD_TOP_K: int = 50
    SEMANTIC_WEIGHT: float = 0.7
    RERANKER_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.5

    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = "sqlite+aiosqlite:///./rag.db"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

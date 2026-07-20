"""本地 Embedding 向量化服务（国内镜像优先）"""
import os
from ..core.config import get_settings

settings = get_settings()

_embedding_model = None


def _get_model():
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model

    # 国内环境优先使用 modelscope 镜像
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RuntimeError("sentence-transformers 未安装，仅支持关键词检索")

    # 按顺序尝试加载模型（从小到大）
    candidates = [
        "BAAI/bge-small-zh-v1.5",
        "BAAI/bge-large-zh-v1.5",
        "BAAI/bge-m3",
    ]

    for model_name in candidates:
        try:
            print(f"[Embedding] 尝试加载: {model_name} ...")
            _embedding_model = SentenceTransformer(model_name)
            dim = _embedding_model.get_sentence_embedding_dimension()
            print(f"[Embedding] 成功加载 {model_name}，维度: {dim}")
            return _embedding_model
        except Exception as e:
            print(f"[Embedding] {model_name} 加载失败: {e}")
            continue

    raise RuntimeError("所有 Embedding 模型加载失败")


def _extract_keywords(text: str, min_len: int = 2) -> list[str]:
    """从中文/英文查询中提取关键词"""
    import re
    # 去除标点，保留字母数字和中文
    puncts = r'？?！!，,。.、；;：:（）()【】[]\"\' \t\n\r'
    cleaned = re.sub('[' + puncts + ']+', ' ', text).strip()

    # 分离英文单词和中文片段
    parts = re.split(r'([a-zA-Z]+)', cleaned)
    keywords = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if re.match(r'^[a-zA-Z]+$', part):
            # 英文单词：保留完整词 + 小写形式
            if len(part) >= min_len:
                keywords.append(part)
                keywords.append(part.lower())
        else:
            # 中文：生成 bigram 和 trigram
            for n in [3, 2]:
                for i in range(len(part) - n + 1):
                    kw = part[i:i+n]
                    if len(kw) >= min_len:
                        keywords.append(kw)

    # 去重并限制数量
    seen = set()
    result = []
    for kw in keywords:
        if kw not in seen and len(kw) >= min_len:
            seen.add(kw)
            result.append(kw)
    return result[:15]


def embed_text(text: str) -> list[float]:
    model = _get_model()
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


def embed_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    model = _get_model()
    vecs = model.encode(texts, normalize_embeddings=True, batch_size=batch_size)
    return vecs.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    import numpy as np
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

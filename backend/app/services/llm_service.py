"""DeepSeek API LLM 服务"""
import httpx
from ..core.config import get_settings

settings = get_settings()

DEEPSEEK_BASE = "https://api.deepseek.com"
DEEPSEEK_CHAT = f"{DEEPSEEK_BASE}/v1/chat/completions"

SYSTEM_PROMPT = """你是一个企业级智能知识库助手。严格按以下规则回答：

1. 【最重要】只使用参考资料中明确包含的信息，绝对不要编造或猜测
2. 如果资料中没有答案，直接说"根据现有资料未找到相关信息"，不要补充任何内容
3. 回答时要注明具体来源文档名称
4. 回答简洁准确，使用Markdown格式
5. 对于技术参数、版本号等细节，原文照搬不要修改
6. 不要回答资料中未涉及的内容，哪怕是常识"""


async def generate_answer(query: str, context: str, sources: list[dict]) -> str:
    """调用 DeepSeek 生成答案"""
    if not context.strip():
        return "根据现有资料未找到相关信息，建议上传相关文档后重试。"

    sources_text = ""
    for i, s in enumerate(sources, 1):
        sources_text += f"\n[{i}] 来源: {s.get('doc_name', '未知')} | 页码: {s.get('page', 'N/A')} | 相关度: {s.get('score', 0)}\n"

    user_message = f"""参考资料：
{context}

参考来源列表：
{sources_text}

用户问题：{query}

请根据以上参考资料回答问题："""

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(
                DEEPSEEK_CHAT,
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": settings.LLM_TEMPERATURE,
                    "max_tokens": settings.LLM_MAX_TOKENS,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            return f"LLM 调用失败 (HTTP {e.response.status_code}): {e.response.text[:200]}"
        except Exception as e:
            return f"LLM 调用异常: {str(e)}"

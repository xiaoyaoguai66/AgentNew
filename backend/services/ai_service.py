import asyncio
import json
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from config.settings import get_settings
from prompts.news_assistant import PROMPT_VERSION, build_chat_messages
from schemas.ai import AiChatMessage, AiChatRequest, AiSourceItem
from services.query_analysis_service import QueryAnalysis


settings = get_settings()


def _extract_reply(payload: dict) -> str:
    if payload.get("choices"):
        choice = payload["choices"][0]
        message = choice.get("message", {})
        if isinstance(message, dict) and message.get("content"):
            return message["content"]
        delta = choice.get("delta", {})
        if isinstance(delta, dict) and delta.get("content"):
            return delta["content"]

    output = payload.get("output")
    if isinstance(output, dict) and output.get("text"):
        return output["text"]

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="模型服务返回了无法解析的响应。",
    )


def _request_completion(messages: list[AiChatMessage]) -> str:
    if not settings.llm_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 服务尚未配置，请在 .env 中设置 LLM_API_KEY。",
        )

    body = json.dumps(
        {
            "model": settings.llm_model,
            "messages": [message.model_dump() for message in messages],
            "stream": False,
        }
    ).encode("utf-8")
    request = Request(
        settings.llm_base_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.llm_api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.llm_request_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return _extract_reply(payload)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"模型服务调用失败: {detail or exc.reason}",
        ) from exc
    except (TimeoutError, SocketTimeout) as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"AI 服务超时，超过 {settings.llm_request_timeout_seconds} 秒，请稍后重试。",
        ) from exc
    except URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"模型服务不可达: {exc.reason}",
        ) from exc


def prepare_chat_messages(
    data: AiChatRequest,
    sources: list[AiSourceItem],
    query_analysis: QueryAnalysis | None = None,
) -> list[AiChatMessage]:
    return build_chat_messages(
        question=data.question,
        history=data.history,
        mode=data.mode,
        time_range=data.time_range,
        category=data.category,
        sources=sources,
        query_analysis=query_analysis,
        memory_summary=data.memory_summary,
    )


async def generate_reply(messages: list[AiChatMessage]) -> str:
    return await asyncio.to_thread(_request_completion, messages)


async def chat(
    data: AiChatRequest,
    sources: list[AiSourceItem],
    query_analysis: QueryAnalysis | None = None,
) -> str:
    messages = prepare_chat_messages(data, sources, query_analysis=query_analysis)
    return await generate_reply(messages)

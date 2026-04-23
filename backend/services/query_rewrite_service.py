import asyncio
import json
import re
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.settings import get_settings


settings = get_settings()
QUERY_REWRITE_TIMEOUT_SECONDS = min(max(settings.llm_request_timeout_seconds, 6), 15)


def needs_web_query_rewrite(question: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", question or ""))


def _extract_reply_text(payload: dict) -> str:
    if payload.get("choices"):
        choice = payload["choices"][0]
        message = choice.get("message", {})
        if isinstance(message, dict) and message.get("content"):
            return message["content"]

    output = payload.get("output")
    if isinstance(output, dict) and output.get("text"):
        return output["text"]

    return ""


def _sanitize_rewritten_query(content: str) -> str:
    cleaned = (content or "").strip().strip("`").strip()
    cleaned = cleaned.replace("\r", "\n").split("\n")[0]
    cleaned = re.sub(r"^(english search query|search query|query)\s*[:：-]\s*", "", cleaned, flags=re.I)
    cleaned = cleaned.strip("\"' ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:160]


def _request_web_query_rewrite(question: str) -> str:
    if not settings.llm_api_key:
        return ""

    body = json.dumps(
        {
            "model": settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You rewrite a user's news question into a concise English web search query for a search engine. "
                        "Keep key entities, events, dates, and locations. Return only one English query line with no explanation."
                    ),
                },
                {
                    "role": "user",
                    "content": question[:400],
                },
            ],
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
        with urlopen(request, timeout=QUERY_REWRITE_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return _sanitize_rewritten_query(_extract_reply_text(payload))
    except (HTTPError, URLError, TimeoutError, SocketTimeout, json.JSONDecodeError):
        return ""


async def rewrite_for_web_search(question: str) -> str:
    if not needs_web_query_rewrite(question):
        return question

    rewritten = await asyncio.to_thread(_request_web_query_rewrite, question)
    return rewritten or ""

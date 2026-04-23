import asyncio
import json
import logging
from datetime import datetime
from socket import timeout as SocketTimeout
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from config.settings import get_settings
from schemas.ai import AiSourceItem
from services import query_rewrite_service


logger = logging.getLogger(__name__)
settings = get_settings()

TIME_RANGE_MAP = {
    "24h": "day",
    "7d": "week",
}

SEARCH_DEPTH_ALLOWLIST = {"advanced", "basic", "fast", "ultra-fast"}


class TavilyInvalidQueryError(Exception):
    pass


def is_enabled() -> bool:
    return bool(settings.tavily_api_key)


def _resolve_topic(category: str) -> str:
    if category == "finance":
        return "finance"
    return "news"


def _resolve_search_depth() -> str:
    if settings.tavily_search_depth in SEARCH_DEPTH_ALLOWLIST:
        return settings.tavily_search_depth
    return "basic"


def _build_payload(question: str, category: str, time_range: str) -> dict:
    payload = {
        "query": question,
        "topic": _resolve_topic(category),
        "search_depth": _resolve_search_depth(),
        "max_results": max(1, min(settings.tavily_max_results, 5)),
        "include_answer": False,
        "include_raw_content": False,
        "include_usage": False,
        "auto_parameters": False,
    }

    mapped_time_range = TIME_RANGE_MAP.get(time_range)
    if mapped_time_range:
        payload["time_range"] = mapped_time_range

    return payload


def _request_search(question: str, category: str, time_range: str) -> dict:
    if not is_enabled():
        return {"results": []}

    body = json.dumps(_build_payload(question, category, time_range)).encode("utf-8")
    request = Request(
        settings.tavily_base_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.tavily_api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.tavily_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        if exc.code == 400 and "Query is invalid" in detail:
            raise TavilyInvalidQueryError(detail)
        logger.warning("tavily search failed: %s", detail or exc.reason)
        return {"results": []}
    except (TimeoutError, SocketTimeout):
        logger.warning("tavily search timed out after %s seconds", settings.tavily_timeout_seconds)
        return {"results": []}
    except URLError as exc:
        logger.warning("tavily search unavailable: %s", exc.reason)
        return {"results": []}
    except json.JSONDecodeError:
        logger.warning("tavily search returned invalid json")
        return {"results": []}


def _parse_result(item: dict) -> AiSourceItem | None:
    title = (item.get("title") or "").strip()
    url = (item.get("url") or "").strip()
    snippet = " ".join((item.get("content") or "").split())
    raw_content = " ".join((item.get("raw_content") or "").split())

    if not title and not url:
        return None

    if not title:
        title = url

    if not snippet:
        snippet = raw_content or title

    domain = urlparse(url).netloc or None
    published_time = _coerce_publish_time(item.get("published_date") or item.get("published_at"))

    return AiSourceItem(
        sourceType="web",
        title=title,
        snippet=snippet[:220],
        url=url or None,
        domain=domain,
        publishTime=published_time,
        retrievalTags=["web"],
        score=float(item.get("score") or 0.0),
    )


def _coerce_publish_time(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        normalized = value.strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

    return None


async def search_news_sources(
    question: str,
    category: str,
    time_range: str,
) -> list[AiSourceItem]:
    if not is_enabled():
        return []

    search_queries: list[str] = []
    rewritten_query = ""

    if query_rewrite_service.needs_web_query_rewrite(question):
        rewritten_query = await query_rewrite_service.rewrite_for_web_search(question)
        if rewritten_query and rewritten_query.lower() != question.lower():
            search_queries.append(rewritten_query)

    if question not in search_queries:
        search_queries.append(question)

    for search_query in search_queries:
        try:
            payload = await asyncio.wait_for(
                asyncio.to_thread(_request_search, search_query, category, time_range),
                timeout=max(settings.tavily_timeout_seconds + 1, 2),
            )
        except TavilyInvalidQueryError:
            logger.warning("tavily rejected query: %s", search_query)
            continue
        except TimeoutError:
            logger.warning("tavily async search timed out after %s seconds", settings.tavily_timeout_seconds)
            return []

        results = payload.get("results") or []
        sources: list[AiSourceItem] = []
        for item in results:
            source = _parse_result(item)
            if source:
                sources.append(source)

        if sources:
            if rewritten_query and search_query == rewritten_query:
                logger.info("tavily web query rewritten from %r to %r", question, rewritten_query)
            return sources

    return []

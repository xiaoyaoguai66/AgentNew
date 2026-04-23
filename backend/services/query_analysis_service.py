from dataclasses import dataclass
import re


INTENT_TERMS = {
    "timeline": ("时间线", "梳理", "发展", "脉络", "timeline"),
    "compare": ("对比", "比较", "差异", "异同", "compare"),
    "summary": ("总结", "概览", "盘点", "汇总", "brief"),
}

LOCAL_SCOPE_TERMS = (
    "本地新闻",
    "新闻库",
    "站内",
    "项目里",
    "项目内",
    "本站",
    "收藏",
    "历史",
    "这篇新闻",
    "这条新闻",
    "详情页",
    "仅基于本地",
)

WEB_SCOPE_TERMS = (
    "联网",
    "网页",
    "web",
    "官网",
    "官方",
    "搜索",
    "搜一个",
    "查一个",
    "外网",
)

HIGH_FRESHNESS_TERMS = (
    "最新",
    "刚刚",
    "实时",
    "现在",
    "目前",
    "今天",
    "今日",
    "最新消息",
    "最新进展",
)

MEDIUM_FRESHNESS_TERMS = (
    "最近",
    "近期",
    "本周",
    "本月",
    "近几天",
    "近一周",
    "近两周",
    "最近几天",
    "近期变化",
    "阶段性",
)

EN_STOPWORDS = {"what", "when", "where", "which", "about", "with", "from", "that", "this"}
ZH_STOPWORDS = {"最近", "新闻", "这个", "那个", "哪些", "什么", "为什么", "情况", "现在"}


@dataclass(slots=True)
class QueryAnalysis:
    intent: str
    freshness_need: str
    scope_preference: str
    keyword_hints: list[str]
    reason: str


def get_runtime_status() -> dict:
    return {
        "queryAnalysisEnabled": True,
        "queryAnalysisStrategy": "heuristic-query-analysis",
    }


def _normalize_text(content: str) -> str:
    return re.sub(r"\s+", " ", (content or "").strip().lower())


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _extract_terms(content: str) -> list[str]:
    parts = re.findall(r"[0-9a-z]+|[\u4e00-\u9fff]+", _normalize_text(content))
    terms: list[str] = []

    for part in parts:
        if len(part) < 2:
            continue
        if part.isascii():
            if part not in EN_STOPWORDS:
                terms.append(part)
            continue
        if part in ZH_STOPWORDS:
            continue
        if len(part) <= 4:
            terms.append(part)
            continue
        terms.append(part[:4])
        terms.append(part[-4:])

    unique_terms: list[str] = []
    for item in terms:
        if item not in unique_terms:
            unique_terms.append(item)
    return unique_terms[:6]


def _detect_intent(normalized_question: str, mode: str) -> str:
    for intent, terms in INTENT_TERMS.items():
        if any(term in normalized_question for term in terms):
            return intent

    if mode == "timeline":
        return "timeline"
    if mode == "compare":
        return "compare"
    if mode == "brief":
        return "summary"
    return "fact"


def _detect_scope(normalized_question: str, web_enabled: bool) -> str:
    if _has_any(normalized_question, LOCAL_SCOPE_TERMS):
        return "local"
    if _has_any(normalized_question, WEB_SCOPE_TERMS):
        return "web"
    if web_enabled:
        return "hybrid"
    return "local"


def _detect_freshness(normalized_question: str, time_range: str) -> str:
    if time_range == "24h":
        return "high"
    if time_range == "7d":
        return "medium"
    if _has_any(normalized_question, HIGH_FRESHNESS_TERMS):
        return "high"
    if _has_any(normalized_question, MEDIUM_FRESHNESS_TERMS):
        return "medium"
    return "low"


def analyze_query(
    question: str,
    category: str,
    time_range: str,
    mode: str,
    web_enabled: bool,
) -> QueryAnalysis:
    normalized_question = _normalize_text(question)
    intent = _detect_intent(normalized_question, mode)
    scope_preference = _detect_scope(normalized_question, web_enabled)
    freshness_need = _detect_freshness(normalized_question, time_range)
    keyword_hints = _extract_terms(question)

    reason = (
        f"问题更偏向{intent}，时效性需求为{freshness_need}，范围偏好为{scope_preference}，"
        f"当前主题为{category}。"
    )

    return QueryAnalysis(
        intent=intent,
        freshness_need=freshness_need,
        scope_preference=scope_preference,
        keyword_hints=keyword_hints,
        reason=reason,
    )

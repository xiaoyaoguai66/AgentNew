from dataclasses import dataclass
import re
from typing import Literal

from schemas.ai import AiSourceItem
from services.query_analysis_service import QueryAnalysis


RetrievalPlanType = Literal["local-first", "hybrid", "web-first"]
SUPPORTED_RETRIEVAL_PLANS: tuple[RetrievalPlanType, ...] = ("local-first", "hybrid", "web-first")

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

EXPLICIT_WEB_TERMS = (
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

RECENCY_TERMS = (
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

ANALYSIS_TERMS = (
    "梳理",
    "分析",
    "对比",
    "比较",
    "趋势",
    "盘点",
    "影响",
    "怎么看",
    "意味着",
    "解读",
    "复盘",
    "脉络",
    "时间线",
)


@dataclass(slots=True)
class RetrievalPlanDecision:
    plan_type: RetrievalPlanType
    reason: str


def _normalize_text(content: str) -> str:
    return re.sub(r"\s+", " ", (content or "").strip().lower())


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def get_runtime_status() -> dict:
    return {
        "plannerEnabled": True,
        "supportedRetrievalPlans": list(SUPPORTED_RETRIEVAL_PLANS),
        "plannerStrategy": "heuristic-route-planner",
    }


def decide_retrieval_plan(
    question: str,
    category: str,
    time_range: str,
    web_enabled: bool,
    analysis: QueryAnalysis | None = None,
) -> RetrievalPlanDecision:
    normalized_question = _normalize_text(question)
    has_local_scope = _has_any(normalized_question, LOCAL_SCOPE_TERMS)
    has_explicit_web = _has_any(normalized_question, EXPLICIT_WEB_TERMS)
    has_recency_signal = _has_any(normalized_question, RECENCY_TERMS)
    has_analysis_terms = _has_any(normalized_question, ANALYSIS_TERMS)

    if analysis:
        has_local_scope = has_local_scope or analysis.scope_preference == "local"
        has_explicit_web = has_explicit_web or analysis.scope_preference == "web"
        has_recency_signal = has_recency_signal or analysis.freshness_need == "high"
        has_analysis_terms = has_analysis_terms or analysis.intent in {"timeline", "compare"}

    if not web_enabled:
        return RetrievalPlanDecision(
            plan_type="local-first",
            reason="Tavily 未开启，当前只能优先使用本地新闻库完成检索和回答。",
        )

    if has_local_scope:
        return RetrievalPlanDecision(
            plan_type="local-first",
            reason="问题显式限定在站内新闻、收藏或单篇新闻上下文里，更适合先查本地新闻库。",
        )

    if has_explicit_web:
        return RetrievalPlanDecision(
            plan_type="web-first",
            reason="问题显式要求联网、官网或网页搜索，优先走 Web Search 更符合用户预期。",
        )

    if time_range == "24h" and not has_local_scope:
        return RetrievalPlanDecision(
            plan_type="web-first",
            reason="问题聚焦近 24 小时动态，通常更依赖外部最新信息，优先走 Web Search 更稳。",
        )

    if has_recency_signal and category == "general" and not has_analysis_terms:
        return RetrievalPlanDecision(
            plan_type="web-first",
            reason="问题带有明显的最新性信号，且没有限定在本地新闻库内，优先尝试 Web Search。",
        )

    if has_analysis_terms or time_range == "7d" or category != "general":
        return RetrievalPlanDecision(
            plan_type="hybrid",
            reason="问题既需要一定的新鲜度，也需要站内新闻库做补充解释，适合走本地 + Web 的混合检索。",
        )

    return RetrievalPlanDecision(
        plan_type="hybrid",
        reason="当前问题没有明显的单一路径偏好，默认使用混合检索以兼顾本地新闻与外部信息。",
    )


def is_local_result_strong(sources: list[AiSourceItem]) -> bool:
    if not sources:
        return False

    top_score = sources[0].score
    if len(sources) >= 3 and top_score >= 4.6:
        return True
    if len(sources) >= 2 and top_score >= 6.5:
        return True
    return top_score >= 8.5


def is_web_result_strong(sources: list[AiSourceItem]) -> bool:
    if not sources:
        return False

    top_score = sources[0].score
    if len(sources) >= 3 and top_score >= 0.42:
        return True
    if len(sources) >= 2 and top_score >= 0.55:
        return True
    return top_score >= 0.68

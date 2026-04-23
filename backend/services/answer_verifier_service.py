from dataclasses import dataclass
import re

from config.settings import get_settings
from schemas.ai import AiSourceItem


settings = get_settings()


ASSERTIVE_PATTERNS = (
    "可以确定",
    "毫无疑问",
    "已经证实",
    "必然会",
    "一定会",
    "可以直接得出结论",
    "confirmed",
    "definitely",
    "certainly",
)
CITATION_PATTERN = re.compile(r"\[\d+\]")


@dataclass(slots=True)
class VerificationResult:
    status: str
    reason: str
    evidence_level: str
    guardrail_applied: bool
    reply: str


def get_runtime_status() -> dict:
    return {
        "verifierEnabled": True,
        "verifierStrategy": "rule-based-post-verifier",
    }


def _has_cross_source_support(sources: list[AiSourceItem]) -> bool:
    return len({source.source_type for source in sources}) >= 2


def _has_local_dual_signal(sources: list[AiSourceItem]) -> bool:
    for source in sources:
        tags = set(source.retrieval_tags or [])
        if source.source_type == "local" and "lexical" in tags and "vector" in tags:
            return True
    return False


def _estimate_evidence_level(confidence: float, sources: list[AiSourceItem]) -> str:
    if not sources:
        return "none"

    source_count = len(sources)
    if confidence >= 0.76 and source_count >= 3 and (_has_cross_source_support(sources) or _has_local_dual_signal(sources)):
        return "strong"
    if confidence >= 0.56 and source_count >= 2:
        return "moderate"
    return "weak"


def _contains_assertive_claims(reply: str) -> bool:
    lowered = (reply or "").lower()
    return any(pattern in reply or pattern in lowered for pattern in ASSERTIVE_PATTERNS)


def _has_citations(reply: str) -> bool:
    return bool(CITATION_PATTERN.search(reply or ""))


def _build_source_summary(sources: list[AiSourceItem], limit: int = 2) -> str:
    titles = [source.title.strip() for source in sources if source.title.strip()]
    if not titles:
        return "当前证据还不足以支撑稳定结论。"

    selected = titles[:limit]
    if len(selected) == 1:
        return f"当前更可靠的线索主要来自《{selected[0]}》。"
    return f"当前更可靠的线索主要集中在《{selected[0]}》和《{selected[1]}》。"


def _build_low_confidence_reply(reply: str, sources: list[AiSourceItem]) -> str:
    safe_reply = (reply or "").strip()
    if safe_reply and not safe_reply.endswith(("。", "！", "？", ".", "!", "?")):
        safe_reply = f"{safe_reply}。"

    caution = "当前证据支撑偏弱，下面内容应视为保守判断，不宜直接当作确定结论。"
    source_summary = _build_source_summary(sources)
    note = "如果你愿意，我可以继续缩小时间范围、指定主题，或只基于本地新闻/只基于 Web 来源再做一次回答。"

    if not safe_reply:
        return f"{caution}\n\n{source_summary}\n\n{note}"

    return f"{caution}\n\n{safe_reply}\n\n{source_summary}\n\n{note}"


def _build_no_evidence_reply() -> str:
    return (
        "当前检索到的证据不足，我先不直接给出确定结论，以避免把猜测写成事实。"
        "\n\n你可以尝试缩小时间范围、指定主题，或换一个更明确的关键词后再问一次。"
    )


def verify_answer(
    question: str,
    reply: str,
    sources: list[AiSourceItem],
    confidence: float,
    retrieval_plan: str,
) -> VerificationResult:
    del question, retrieval_plan

    if not sources:
        return VerificationResult(
            status="refused",
            reason="当前没有足够证据支撑回答，已触发无证据拒答。",
            evidence_level="none",
            guardrail_applied=True,
            reply=_build_no_evidence_reply(),
        )

    evidence_level = _estimate_evidence_level(confidence, sources)
    has_citations = _has_citations(reply)
    has_assertive_claims = _contains_assertive_claims(reply)
    single_weak_web = len(sources) == 1 and sources[0].source_type == "web"
    single_local_source = len(sources) == 1 and sources[0].source_type == "local"

    if confidence < settings.ai_refusal_confidence_threshold and evidence_level == "weak":
        return VerificationResult(
            status="guarded",
            reason="证据过弱且置信度过低，已切换为保守回答。",
            evidence_level=evidence_level,
            guardrail_applied=True,
            reply=_build_low_confidence_reply(reply, sources),
        )

    if evidence_level == "weak" and (
        confidence < settings.ai_low_confidence_threshold
        or has_assertive_claims
        or single_weak_web
        or single_local_source
    ):
        return VerificationResult(
            status="guarded",
            reason="当前来源数量或稳定性不足，已自动加上低置信度保护。",
            evidence_level=evidence_level,
            guardrail_applied=True,
            reply=_build_low_confidence_reply(reply, sources),
        )

    if evidence_level == "moderate" and not has_citations and len((reply or "").strip()) >= 220:
        return VerificationResult(
            status="guarded",
            reason="回答较长但引用不够明确，已附加保守说明。",
            evidence_level=evidence_level,
            guardrail_applied=True,
            reply=(
                f"{reply.rstrip()}\n\n"
                "注：以上结论基于当前检索到的证据整理，若需要精确核验，请继续查看下方来源。"
            ),
        )

    return VerificationResult(
        status="accepted",
        reason="当前回答已通过后置校验。",
        evidence_level=evidence_level,
        guardrail_applied=False,
        reply=reply,
    )

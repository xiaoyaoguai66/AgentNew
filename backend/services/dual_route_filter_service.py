from datetime import datetime, timezone
import re

from schemas.ai import AiSourceItem


EN_STOPWORDS = {"what", "when", "where", "which", "about", "with", "from", "that", "this"}
ZH_STOPWORDS = {"最近", "新闻", "这个", "那个", "哪些", "什么", "为什么", "情况", "现在"}

LOCAL_LIMITS = {"local-first": 5, "hybrid": 4, "web-first": 3}
WEB_LIMITS = {"local-first": 2, "hybrid": 4, "web-first": 5}
LOCAL_THRESHOLDS = {"local-first": 0.26, "hybrid": 0.22, "web-first": 0.28}
WEB_THRESHOLDS = {"local-first": 0.20, "hybrid": 0.20, "web-first": 0.18}
MAX_WEB_PER_DOMAIN = 2


def get_runtime_status() -> dict:
    return {
        "dualRouteFilterStrategy": "route-aware-filtering",
        "finalRerankStrategy": "plan-aware-cross-source",
    }


def _normalize_text(content: str | None) -> str:
    return re.sub(r"\s+", " ", (content or "").strip()).lower()


def _compact_text(content: str | None) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", _normalize_text(content))


def _build_bigrams(content: str | None) -> set[str]:
    compact = _compact_text(content)
    if len(compact) < 2:
        return {compact} if compact else set()
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


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
        for size in (2, 3):
            for index in range(min(len(part) - size + 1, 4)):
                terms.append(part[index : index + size])

    unique_terms: list[str] = []
    for item in terms:
        if item not in unique_terms:
            unique_terms.append(item)
    return unique_terms[:12]


def _normalize_timestamp(value: datetime | None) -> datetime | None:
    if not value:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _normalize_base_score(source: AiSourceItem) -> float:
    if source.source_type == "local":
        return min(max(source.score, 0.0), 12.0) / 12.0
    return min(max(source.score, 0.0), 1.0)


def _compute_overlap_score(question_terms: list[str], question_bigrams: set[str], source: AiSourceItem) -> float:
    combined = f"{source.title} {source.snippet}".strip()
    normalized = _normalize_text(combined)
    title = _normalize_text(source.title)
    term_hits = sum(1 for term in question_terms if term in normalized)
    title_hits = sum(1 for term in question_terms if term in title)
    term_ratio = term_hits / len(question_terms) if question_terms else 0.0
    title_ratio = title_hits / len(question_terms) if question_terms else 0.0

    candidate_bigrams = _build_bigrams(combined)
    bigram_ratio = len(question_bigrams & candidate_bigrams) / len(question_bigrams) if question_bigrams else 0.0
    return term_ratio * 0.16 + title_ratio * 0.08 + bigram_ratio * 0.08


def _compute_recency_score(source: AiSourceItem, time_range: str) -> float:
    publish_time = _normalize_timestamp(source.publish_time)
    if not publish_time:
        return -0.03 if time_range == "24h" else 0.0

    now = datetime.utcnow()
    age_seconds = max((now - publish_time).total_seconds(), 0.0)
    age_hours = age_seconds / 3600
    age_days = age_hours / 24

    if time_range == "24h":
        return max(0.0, 0.12 - min(age_hours, 48) / 48 * 0.12)
    if time_range == "7d":
        return max(0.0, 0.08 - min(age_days, 14) / 14 * 0.08)
    return max(0.0, 0.04 - min(age_days, 30) / 30 * 0.04)


def _local_signal_bonus(source: AiSourceItem) -> float:
    tags = set(source.retrieval_tags or [])
    if "lexical" in tags and "vector" in tags:
        return 0.18
    if "vector" in tags:
        return 0.10
    if "lexical" in tags:
        return 0.06
    return 0.0


def _web_signal_bonus(source: AiSourceItem) -> float:
    bonus = 0.0
    if source.domain:
        bonus += 0.04
    if len((source.snippet or "").strip()) >= 60:
        bonus += 0.03
    if source.publish_time:
        bonus += 0.02
    return bonus


def _route_plan_prior(source: AiSourceItem, retrieval_plan: str) -> float:
    if retrieval_plan == "local-first":
        return 0.06 if source.source_type == "local" else -0.02
    if retrieval_plan == "web-first":
        return 0.06 if source.source_type == "web" else -0.02
    return 0.02


def _route_quality_score(
    question_terms: list[str],
    question_bigrams: set[str],
    source: AiSourceItem,
    retrieval_plan: str,
    time_range: str,
) -> float:
    score = _normalize_base_score(source) * 0.48
    score += _compute_overlap_score(question_terms, question_bigrams, source)
    score += _compute_recency_score(source, time_range)
    score += _route_plan_prior(source, retrieval_plan)
    if source.source_type == "local":
        score += _local_signal_bonus(source)
    else:
        score += _web_signal_bonus(source)
    return round(score, 4)


def _filter_route_sources(
    question_terms: list[str],
    question_bigrams: set[str],
    sources: list[AiSourceItem],
    retrieval_plan: str,
    time_range: str,
    source_type: str,
) -> list[AiSourceItem]:
    if not sources:
        return []

    limit = LOCAL_LIMITS[retrieval_plan] if source_type == "local" else WEB_LIMITS[retrieval_plan]
    threshold = LOCAL_THRESHOLDS[retrieval_plan] if source_type == "local" else WEB_THRESHOLDS[retrieval_plan]

    scored = [
        (
            _route_quality_score(question_terms, question_bigrams, source, retrieval_plan, time_range),
            source,
        )
        for source in sources
    ]
    scored.sort(
        key=lambda item: (
            -item[0],
            item[1].publish_time.isoformat() if item[1].publish_time else "",
            -(item[1].news_id or 0),
        )
    )

    kept: list[AiSourceItem] = []
    domain_counts: dict[str, int] = {}

    for route_score, source in scored:
        if route_score < threshold and kept:
            continue

        if source_type == "web" and source.domain:
            if domain_counts.get(source.domain, 0) >= MAX_WEB_PER_DOMAIN:
                continue
            domain_counts[source.domain] = domain_counts.get(source.domain, 0) + 1

        kept.append(source)
        if len(kept) >= limit:
            break

    if kept:
        return kept

    return [scored[0][1]]


def filter_dual_route_sources(
    question: str,
    retrieval_plan: str,
    time_range: str,
    local_sources: list[AiSourceItem],
    web_sources: list[AiSourceItem],
) -> tuple[list[AiSourceItem], list[AiSourceItem]]:
    question_terms = _extract_terms(question)
    question_bigrams = _build_bigrams(question)

    filtered_local = _filter_route_sources(
        question_terms=question_terms,
        question_bigrams=question_bigrams,
        sources=local_sources,
        retrieval_plan=retrieval_plan,
        time_range=time_range,
        source_type="local",
    )
    filtered_web = _filter_route_sources(
        question_terms=question_terms,
        question_bigrams=question_bigrams,
        sources=web_sources,
        retrieval_plan=retrieval_plan,
        time_range=time_range,
        source_type="web",
    )
    return filtered_local, filtered_web

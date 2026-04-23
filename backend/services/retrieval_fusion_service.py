from dataclasses import dataclass
from datetime import datetime, timezone
import re

from schemas.ai import AiSourceItem


MAX_FUSED_SOURCES = 6
MIN_FUSED_SCORE = 0.28
MAX_WEB_PER_DOMAIN = 2
TYPE_LIMITS = {
    "local-first": {"local": 4, "web": 2},
    "hybrid": {"local": 3, "web": 3},
    "web-first": {"local": 2, "web": 4},
}

EN_STOPWORDS = {"what", "when", "where", "which", "about", "with", "from", "that", "this"}
ZH_STOPWORDS = {"最近", "新闻", "这个", "那个", "哪些", "什么", "为什么", "情况", "现在"}


@dataclass(slots=True)
class RankedSource:
    source: AiSourceItem
    fused_score: float
    raw_score: float
    source_type: str
    domain: str | None


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


def _normalize_source_score(source: AiSourceItem) -> float:
    if source.source_type == "local":
        return min(max(source.score, 0.0), 12.0) / 12.0
    return min(max(source.score, 0.0), 1.0)


def _compute_overlap_score(question_terms: list[str], question_bigrams: set[str], source: AiSourceItem) -> float:
    title = _normalize_text(source.title)
    snippet = _normalize_text(source.snippet)
    combined = f"{title} {snippet}".strip()

    term_hits = sum(1 for term in question_terms if term in combined)
    title_hits = sum(1 for term in question_terms if term in title)
    term_ratio = term_hits / len(question_terms) if question_terms else 0.0
    title_ratio = title_hits / len(question_terms) if question_terms else 0.0

    candidate_bigrams = _build_bigrams(combined)
    bigram_ratio = len(question_bigrams & candidate_bigrams) / len(question_bigrams) if question_bigrams else 0.0

    return term_ratio * 0.18 + title_ratio * 0.12 + bigram_ratio * 0.10


def _compute_recency_score(source: AiSourceItem, time_range: str) -> float:
    publish_time = _normalize_timestamp(source.publish_time)
    if not publish_time:
        return 0.0

    now = datetime.utcnow()
    age_seconds = max((now - publish_time).total_seconds(), 0.0)
    age_hours = age_seconds / 3600
    age_days = age_hours / 24

    if time_range == "24h":
        return max(0.0, 0.16 - min(age_hours, 48) / 48 * 0.16)
    if time_range == "7d":
        return max(0.0, 0.12 - min(age_days, 14) / 14 * 0.12)
    return max(0.0, 0.08 - min(age_days, 30) / 30 * 0.08)


def _source_prior(source: AiSourceItem, category: str, retrieval_plan: str) -> float:
    base = 0.06 if source.source_type == "local" else 0.04

    if retrieval_plan == "local-first":
        base += 0.04 if source.source_type == "local" else -0.01
    elif retrieval_plan == "web-first":
        base += 0.04 if source.source_type == "web" else -0.01

    if category != "general" and source.source_type == "local":
        base += 0.02
    if source.source_type == "local":
        tags = set(source.retrieval_tags or [])
        if "lexical" in tags and "vector" in tags:
            base += 0.05
        elif "vector" in tags:
            base += 0.03
        elif "lexical" in tags:
            base += 0.01
    elif source.domain:
        base += 0.01
    return base


def get_runtime_status() -> dict:
    return {
        "finalRerankStrategy": "plan-aware-cross-source",
    }


def _coherence_bonus(candidate: AiSourceItem, others: list[AiSourceItem]) -> float:
    candidate_terms = set(_extract_terms(f"{candidate.title} {candidate.snippet}"))
    if not candidate_terms:
        return 0.0

    best_bonus = 0.0
    for other in others:
        if other.source_type == candidate.source_type:
            continue
        shared_terms = len(candidate_terms & set(_extract_terms(f"{other.title} {other.snippet}")))
        if shared_terms >= 3:
            best_bonus = max(best_bonus, 0.08)
        elif shared_terms >= 2:
            best_bonus = max(best_bonus, 0.05)
        elif shared_terms >= 1:
            best_bonus = max(best_bonus, 0.02)
    return best_bonus


def _deduplicate_candidates(ranked_items: list[RankedSource]) -> list[RankedSource]:
    deduplicated: list[RankedSource] = []
    seen_keys: set[str] = set()

    for item in ranked_items:
        source = item.source
        if source.source_type == "local" and source.news_id is not None:
            key = f"local:{source.news_id}"
        elif source.url:
            key = f"web:{source.url}"
        else:
            key = f"title:{_compact_text(source.title)}"

        if key in seen_keys:
            continue

        seen_keys.add(key)
        deduplicated.append(item)

    return deduplicated


def _select_balanced_sources(ranked_items: list[RankedSource], limit: int, retrieval_plan: str) -> list[RankedSource]:
    if not ranked_items:
        return []

    selected: list[RankedSource] = []
    selected_keys: set[str] = set()
    type_counts = {"local": 0, "web": 0}
    domain_counts: dict[str, int] = {}
    type_limits = TYPE_LIMITS.get(retrieval_plan, TYPE_LIMITS["hybrid"])

    local_items = [item for item in ranked_items if item.source_type == "local"]
    web_items = [item for item in ranked_items if item.source_type == "web"]
    has_hybrid_candidates = bool(local_items and web_items)

    mandatory_items: list[RankedSource] = []
    if has_hybrid_candidates:
        if retrieval_plan == "web-first":
            mandatory_items.extend([web_items[0], local_items[0]])
        elif retrieval_plan == "local-first":
            mandatory_items.extend([local_items[0], web_items[0]])
        else:
            mandatory_items.extend([local_items[0], web_items[0]])

    def add_item(item: RankedSource) -> None:
        source = item.source
        key = f"{source.source_type}:{source.news_id or source.url or source.title}"
        if key in selected_keys or len(selected) >= limit:
            return

        if has_hybrid_candidates and type_counts[source.source_type] >= type_limits[source.source_type]:
            return

        if source.source_type == "web" and item.domain:
            if domain_counts.get(item.domain, 0) >= MAX_WEB_PER_DOMAIN:
                return
            domain_counts[item.domain] = domain_counts.get(item.domain, 0) + 1

        selected.append(item)
        selected_keys.add(key)
        type_counts[source.source_type] += 1

    for item in sorted(mandatory_items, key=lambda candidate: candidate.fused_score, reverse=True):
        add_item(item)

    for item in ranked_items:
        add_item(item)
        if len(selected) >= limit:
            break

    return selected


def fuse_sources(
    question: str,
    category: str,
    time_range: str,
    local_sources: list[AiSourceItem],
    web_sources: list[AiSourceItem],
    retrieval_plan: str = "hybrid",
    limit: int = MAX_FUSED_SOURCES,
) -> list[AiSourceItem]:
    candidates = list(local_sources) + list(web_sources)
    if not candidates:
        return []

    question_terms = _extract_terms(question)
    question_bigrams = _build_bigrams(question)
    ranked_items: list[RankedSource] = []

    for source in candidates:
        base_score = _normalize_source_score(source)
        fused_score = (
            base_score * 0.52
            + _compute_overlap_score(question_terms, question_bigrams, source)
            + _compute_recency_score(source, time_range)
            + _source_prior(source, category, retrieval_plan)
        )
        fused_score += _coherence_bonus(source, candidates)

        if fused_score < MIN_FUSED_SCORE:
            continue

        ranked_items.append(
            RankedSource(
                source=source.model_copy(update={"score": round(min(fused_score, 0.99), 3)}),
                fused_score=round(min(fused_score, 0.99), 3),
                raw_score=source.score,
                source_type=source.source_type,
                domain=source.domain,
            )
        )

    ranked_items.sort(key=lambda item: (-item.fused_score, item.source_type != "local", -(item.source.news_id or 0)))
    ranked_items = _deduplicate_candidates(ranked_items)
    ranked_items = _select_balanced_sources(ranked_items, limit, retrieval_plan)
    return [item.source for item in ranked_items]


def estimate_confidence(local_sources: list[AiSourceItem], web_sources: list[AiSourceItem], fused_sources: list[AiSourceItem]) -> float:
    if not fused_sources:
        return 0.18

    top_score = fused_sources[0].score
    avg_score = sum(item.score for item in fused_sources[:3]) / min(len(fused_sources), 3)
    confidence = 0.24 + top_score * 0.34 + avg_score * 0.18

    if local_sources:
        confidence += 0.08
    if web_sources:
        confidence += 0.05
    if local_sources and web_sources:
        confidence += 0.07

    confidence += min(len(fused_sources), 6) * 0.025
    return round(max(0.25, min(confidence, 0.94)), 2)

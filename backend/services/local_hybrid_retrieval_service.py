from dataclasses import dataclass, field
from datetime import datetime, timezone
import re

from schemas.ai import AiSourceItem


MAX_LOCAL_HYBRID_CANDIDATES = 8
MIN_LOCAL_HYBRID_SCORE = 1.8
LEXICAL_WEIGHT = 0.42
VECTOR_WEIGHT = 0.38
DUAL_SIGNAL_BONUS = 0.18
LEXICAL_RAW_BONUS = 0.16
VECTOR_RAW_BONUS = 0.14
OVERLAP_BONUS = 0.18
RECENCY_BONUS = 0.08

EN_STOPWORDS = {"what", "when", "where", "which", "about", "with", "from", "that", "this"}
ZH_STOPWORDS = {"最近", "新闻", "这个", "那个", "哪些", "什么", "为什么", "情况", "现在"}


@dataclass(slots=True)
class LocalHybridCandidate:
    source: AiSourceItem
    lexical_rank: int | None = None
    vector_rank: int | None = None
    lexical_score: float = 0.0
    vector_score: float = 0.0
    retrieval_tags: set[str] = field(default_factory=set)


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


def _resolve_candidate_key(source: AiSourceItem) -> str:
    if source.news_id is not None:
        return f"news:{source.news_id}"
    return f"title:{_compact_text(source.title)}:{source.publish_time.isoformat() if source.publish_time else ''}"


def _normalize_timestamp(value: datetime | None) -> datetime | None:
    if not value:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


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
    return min(term_ratio * 0.10 + title_ratio * 0.05 + bigram_ratio * 0.03, OVERLAP_BONUS)


def _compute_recency_score(source: AiSourceItem, time_range: str) -> float:
    publish_time = _normalize_timestamp(source.publish_time)
    if not publish_time:
        return 0.0

    now = datetime.utcnow()
    age_seconds = max((now - publish_time).total_seconds(), 0.0)
    age_hours = age_seconds / 3600
    age_days = age_hours / 24

    if time_range == "24h":
        return max(0.0, RECENCY_BONUS - min(age_hours, 48) / 48 * RECENCY_BONUS)
    if time_range == "7d":
        return max(0.0, 0.06 - min(age_days, 14) / 14 * 0.06)
    return max(0.0, 0.04 - min(age_days, 30) / 30 * 0.04)


def _build_candidates(
    lexical_sources: list[AiSourceItem],
    vector_sources: list[AiSourceItem],
) -> dict[str, LocalHybridCandidate]:
    candidates: dict[str, LocalHybridCandidate] = {}

    for rank, source in enumerate(lexical_sources, start=1):
        key = _resolve_candidate_key(source)
        candidate = candidates.get(key)
        if candidate is None:
            candidate = LocalHybridCandidate(source=source.model_copy())
            candidates[key] = candidate

        candidate.lexical_rank = rank
        candidate.lexical_score = max(candidate.lexical_score, source.score)
        candidate.retrieval_tags.update(source.retrieval_tags or ["lexical"])

        if not candidate.source.snippet and source.snippet:
            candidate.source = candidate.source.model_copy(update={"snippet": source.snippet})

    for rank, source in enumerate(vector_sources, start=1):
        key = _resolve_candidate_key(source)
        candidate = candidates.get(key)
        if candidate is None:
            candidate = LocalHybridCandidate(source=source.model_copy())
            candidates[key] = candidate

        candidate.vector_rank = rank
        candidate.vector_score = max(candidate.vector_score, source.score)
        candidate.retrieval_tags.update(source.retrieval_tags or ["vector"])

        if candidate.lexical_rank is None and source.snippet:
            candidate.source = candidate.source.model_copy(update={"snippet": source.snippet})

    return candidates


def _score_candidate(
    candidate: LocalHybridCandidate,
    question_terms: list[str],
    question_bigrams: set[str],
    time_range: str,
) -> tuple[float, AiSourceItem]:
    score = 0.0
    if candidate.lexical_rank is not None:
        score += LEXICAL_WEIGHT / candidate.lexical_rank
        score += min(candidate.lexical_score, 12.0) / 12.0 * LEXICAL_RAW_BONUS
    if candidate.vector_rank is not None:
        score += VECTOR_WEIGHT / candidate.vector_rank
        score += min(candidate.vector_score, 1.0) * VECTOR_RAW_BONUS
    if candidate.lexical_rank is not None and candidate.vector_rank is not None:
        score += DUAL_SIGNAL_BONUS

    score += _compute_overlap_score(question_terms, question_bigrams, candidate.source)
    score += _compute_recency_score(candidate.source, time_range)

    merged_source = candidate.source.model_copy(
        update={
            "score": round(min(score * 7.0, 12.0), 3),
            "retrievalTags": sorted(candidate.retrieval_tags),
        }
    )
    return score, merged_source


def fuse_local_sources(
    question: str,
    time_range: str,
    lexical_sources: list[AiSourceItem],
    vector_sources: list[AiSourceItem],
    limit: int,
) -> list[AiSourceItem]:
    candidates = _build_candidates(lexical_sources, vector_sources)
    if not candidates:
        return []

    question_terms = _extract_terms(question)
    question_bigrams = _build_bigrams(question)

    ranked: list[tuple[float, AiSourceItem]] = []
    for candidate in candidates.values():
        raw_score, source = _score_candidate(candidate, question_terms, question_bigrams, time_range)
        if source.score < MIN_LOCAL_HYBRID_SCORE:
            continue
        ranked.append((raw_score, source))

    ranked.sort(
        key=lambda item: (
            -item[0],
            "vector" not in item[1].retrieval_tags,
            -(item[1].news_id or 0),
        )
    )
    return [source for _, source in ranked[: min(limit, MAX_LOCAL_HYBRID_CANDIDATES)]]

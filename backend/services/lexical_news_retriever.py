import math
import re
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from crud import news as news_repo
from schemas.ai import AiSourceItem


CANDIDATE_LIMIT = 120
MAX_SOURCES = 4
MIN_RELEVANCE_SCORE = 2.6

CATEGORY_ALIASES = {
    "technology": ["科技", "技术", "互联网", "ai", "人工智能", "数码"],
    "finance": ["财经", "金融", "经济", "商业", "市场", "证券"],
    "international": ["国际", "海外", "全球", "世界", "外交"],
}

EN_STOPWORDS = {"what", "when", "where", "which", "about", "with", "from", "that", "this"}
ZH_STOPWORDS = {"最近", "新闻", "一个", "一下", "这个", "那个", "哪些", "什么", "为什么"}


def _normalize_text(content: str | None) -> str:
    return re.sub(r"\s+", " ", (content or "").strip()).lower()


def _compact_text(content: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", content)


def _build_bigrams(content: str) -> set[str]:
    compact = _compact_text(content)
    if len(compact) < 2:
        return {compact} if compact else set()
    return {compact[index : index + 2] for index in range(len(compact) - 1)}


def _extract_terms(question: str) -> list[str]:
    parts = re.findall(r"[0-9a-z]+|[\u4e00-\u9fff]+", _normalize_text(question))
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


def _resolve_published_after(time_range: str) -> datetime | None:
    now = datetime.now()
    if time_range == "24h":
        return now - timedelta(hours=24)
    if time_range == "7d":
        return now - timedelta(days=7)
    return None


def _resolve_category_ids(category_key: str, categories: list) -> list[int] | None:
    if category_key == "general":
        return None

    aliases = CATEGORY_ALIASES.get(category_key, [])
    matched_ids = [
        category.id
        for category in categories
        if any(alias in (category.name or "").lower() for alias in aliases)
    ]
    return matched_ids or None


def _score_candidate(question_text: str, terms: list[str], question_bigrams: set[str], news_item) -> tuple[float, list[str]]:
    title = _normalize_text(getattr(news_item, "title", ""))
    description = _normalize_text(getattr(news_item, "description", ""))
    content = _normalize_text(getattr(news_item, "content", ""))
    combined = f"{title} {description} {content[:1200]}".strip()

    score = 0.0
    matched_terms: list[str] = []

    if question_text and len(question_text) >= 4 and question_text in combined:
        score += 6.0

    for term in terms:
        if term in title:
            score += 3.6
            matched_terms.append(term)
        elif term in description:
            score += 1.8
            matched_terms.append(term)
        elif term in content:
            score += 1.0
            matched_terms.append(term)

    candidate_bigrams = _build_bigrams(f"{title}{description}{content[:320]}")
    if question_bigrams and candidate_bigrams:
        score += len(question_bigrams & candidate_bigrams) / len(question_bigrams) * 8.0

    publish_time = getattr(news_item, "publish_time", None)
    if publish_time:
        age_days = max((datetime.now() - publish_time).total_seconds() / 86400, 0.0)
        score += max(0.0, 2.0 - age_days / 14)

    score += min(math.log1p(max(int(getattr(news_item, "views", 0)), 0)), 7.0) * 0.25
    return score, list(dict.fromkeys(matched_terms))[:6]


def _build_snippet(news_item, matched_terms: list[str]) -> str:
    raw_text = " ".join(filter(None, [getattr(news_item, "description", ""), getattr(news_item, "content", "")]))
    cleaned = " ".join(raw_text.replace("\n", " ").split())
    if not cleaned:
        return getattr(news_item, "title", "")

    normalized_cleaned = cleaned.lower()
    for term in matched_terms:
        position = normalized_cleaned.find(term)
        if position >= 0:
            start = max(position - 30, 0)
            end = min(position + 90, len(cleaned))
            return cleaned[start:end]

    return cleaned[:120]


async def retrieve_news_sources(
    db: AsyncSession,
    question: str,
    category: str,
    time_range: str,
    limit: int = MAX_SOURCES,
) -> list[AiSourceItem]:
    categories = await news_repo.get_categories(db, 0, 200)
    category_ids = _resolve_category_ids(category, categories)
    published_after = _resolve_published_after(time_range)

    candidates = await news_repo.get_news_candidates(
        db,
        category_ids=category_ids,
        published_after=published_after,
        limit=CANDIDATE_LIMIT,
    )

    if not candidates and category_ids:
        candidates = await news_repo.get_news_candidates(
            db,
            category_ids=None,
            published_after=published_after,
            limit=CANDIDATE_LIMIT,
        )

    question_text = _normalize_text(question)
    terms = _extract_terms(question)
    question_bigrams = _build_bigrams(question_text)

    scored_items: list[tuple[float, AiSourceItem]] = []
    for item in candidates:
        score, matched_terms = _score_candidate(question_text, terms, question_bigrams, item)
        if score < MIN_RELEVANCE_SCORE:
            continue

        snippet = _build_snippet(item, matched_terms)
        source = AiSourceItem(
            sourceType="local",
            newsId=item.id,
            title=item.title,
            snippet=snippet,
            categoryId=item.category_id,
            publishTime=item.publish_time,
            retrievalTags=["lexical"],
            score=round(score, 3),
        )
        scored_items.append((score, source))

    scored_items.sort(key=lambda entry: (-entry[0], -entry[1].news_id))
    return [item for _, item in scored_items[:limit]]

from dataclasses import dataclass
import re

from config.settings import get_settings


settings = get_settings()


@dataclass(slots=True)
class NewsChunkDocument:
    chunk_id: str
    news_id: int
    chunk_index: int
    title: str
    snippet: str
    chunk_text: str
    embedding_text: str
    category_id: int
    publish_time: object | None
    author: str | None
    char_count: int


def _normalize_text(content: str | None) -> str:
    return re.sub(r"\s+", " ", (content or "").strip())


def _split_paragraphs(content: str) -> list[str]:
    normalized = (content or "").replace("\r", "\n")
    paragraphs = [
        _normalize_text(part)
        for part in re.split(r"\n{2,}|\n", normalized)
        if _normalize_text(part)
    ]
    return paragraphs


def _build_segments(news_item) -> list[str]:
    segments: list[str] = []
    title = _normalize_text(getattr(news_item, "title", ""))
    description = _normalize_text(getattr(news_item, "description", ""))
    content = getattr(news_item, "content", "") or ""

    if title:
        segments.append(f"标题：{title}")
    if description:
        segments.append(f"摘要：{description}")

    body_paragraphs = _split_paragraphs(content)
    if body_paragraphs:
        segments.extend(body_paragraphs)
    elif title:
        segments.append(title)

    return segments


def _truncate_tail(content: str, max_chars: int) -> str:
    normalized = _normalize_text(content)
    if len(normalized) <= max_chars:
        return normalized
    return normalized[-max_chars:]


def build_news_chunks(
    news_item,
    chunk_size: int | None = None,
    overlap_chars: int | None = None,
) -> list[NewsChunkDocument]:
    resolved_chunk_size = max(chunk_size or settings.news_chunk_size_chars, 180)
    resolved_overlap = max(min(overlap_chars or settings.news_chunk_overlap_chars, resolved_chunk_size // 2), 0)
    segments = _build_segments(news_item)
    if not segments:
        return []

    chunks: list[NewsChunkDocument] = []
    buffer = ""
    chunk_index = 0

    for segment in segments:
        candidate = f"{buffer}\n{segment}".strip() if buffer else segment
        if buffer and len(candidate) > resolved_chunk_size:
            normalized_chunk = _normalize_text(buffer)
            if normalized_chunk:
                chunks.append(
                    NewsChunkDocument(
                        chunk_id=f"news-{news_item.id}-chunk-{chunk_index}",
                        news_id=news_item.id,
                        chunk_index=chunk_index,
                        title=getattr(news_item, "title", ""),
                        snippet=normalized_chunk[:140],
                        chunk_text=normalized_chunk,
                        embedding_text=f"{getattr(news_item, 'title', '')}\n{normalized_chunk}".strip(),
                        category_id=getattr(news_item, "category_id", 0),
                        publish_time=getattr(news_item, "publish_time", None),
                        author=getattr(news_item, "author", None),
                        char_count=len(normalized_chunk),
                    )
                )
                chunk_index += 1

            overlap_seed = _truncate_tail(normalized_chunk, resolved_overlap)
            buffer = f"{overlap_seed}\n{segment}".strip() if overlap_seed else segment
            continue

        buffer = candidate

    normalized_chunk = _normalize_text(buffer)
    if normalized_chunk:
        chunks.append(
            NewsChunkDocument(
                chunk_id=f"news-{news_item.id}-chunk-{chunk_index}",
                news_id=news_item.id,
                chunk_index=chunk_index,
                title=getattr(news_item, "title", ""),
                snippet=normalized_chunk[:140],
                chunk_text=normalized_chunk,
                embedding_text=f"{getattr(news_item, 'title', '')}\n{normalized_chunk}".strip(),
                category_id=getattr(news_item, "category_id", 0),
                publish_time=getattr(news_item, "publish_time", None),
                author=getattr(news_item, "author", None),
                char_count=len(normalized_chunk),
            )
        )

    return chunks


def get_runtime_status() -> dict:
    return {
        "chunkingReady": True,
        "chunkSizeChars": settings.news_chunk_size_chars,
        "chunkOverlapChars": settings.news_chunk_overlap_chars,
    }

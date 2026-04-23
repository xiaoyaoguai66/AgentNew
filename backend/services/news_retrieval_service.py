from config.settings import get_settings
from schemas.ai import AiSourceItem
from services import lexical_news_retriever, local_hybrid_retrieval_service, vector_news_retriever


settings = get_settings()
SUPPORTED_LOCAL_RETRIEVAL_ENGINES = ("lexical", "hybrid-ready")


def _resolve_local_retrieval_engine() -> str:
    configured = (settings.local_retrieval_engine or "lexical").strip().lower()
    if configured in SUPPORTED_LOCAL_RETRIEVAL_ENGINES:
        return configured
    return "lexical"


LOCAL_HYBRID_CANDIDATE_LIMIT = 8


def get_runtime_status() -> dict:
    vector_status = vector_news_retriever.get_runtime_status()
    local_engine = _resolve_local_retrieval_engine()
    if local_engine == "lexical":
        local_label = "lexical-baseline"
    elif vector_status.get("vectorRetrievalActive"):
        local_label = "lexical-plus-qdrant"
    else:
        local_label = "lexical-plus-vector-ready"
    return {
        "localRetrievalEngine": local_engine,
        "localRetrievalLabel": local_label,
        "localHybridStrategy": "weighted-rrf" if local_engine != "lexical" and vector_status.get("vectorRetrievalActive") else "lexical-only",
        **vector_status,
    }


async def retrieve_news_sources(
    db,
    question: str,
    category: str,
    time_range: str,
    limit: int = 4,
) -> list[AiSourceItem]:
    local_engine = _resolve_local_retrieval_engine()
    candidate_limit = max(limit * 2, LOCAL_HYBRID_CANDIDATE_LIMIT)
    lexical_sources = await lexical_news_retriever.retrieve_news_sources(
        db=db,
        question=question,
        category=category,
        time_range=time_range,
        limit=candidate_limit if local_engine != "lexical" else limit,
    )

    if local_engine == "lexical":
        return lexical_sources

    vector_sources = await vector_news_retriever.retrieve_news_sources(
        db=db,
        question=question,
        category=category,
        time_range=time_range,
        limit=candidate_limit,
    )
    if not vector_sources:
        return lexical_sources[:limit]

    return local_hybrid_retrieval_service.fuse_local_sources(
        question=question,
        time_range=time_range,
        lexical_sources=lexical_sources,
        vector_sources=vector_sources,
        limit=limit,
    )


def estimate_confidence(sources: list[AiSourceItem]) -> float:
    if not sources:
        return 0.18

    top_score = sources[0].score
    avg_score = sum(item.score for item in sources) / len(sources)
    confidence = 0.28 + min(top_score, 14.0) / 18 + min(avg_score, 12.0) / 30 + len(sources) * 0.04
    return round(max(0.25, min(confidence, 0.92)), 2)

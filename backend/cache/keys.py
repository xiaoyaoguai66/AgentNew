def news_categories_key(skip: int, limit: int) -> str:
    return f"news:category:list:{skip}:{limit}"


def news_list_key(category_id: int, page: int, page_size: int) -> str:
    return f"news:list:{category_id}:{page}:{page_size}"


def news_detail_key(news_id: int) -> str:
    return f"news:detail:{news_id}"


def news_related_key(news_id: int) -> str:
    return f"news:related:{news_id}"


def news_views_delta_key(news_id: int) -> str:
    return f"news:views:delta:{news_id}"


def news_views_delta_pattern() -> str:
    return "news:views:delta:*"


def news_hot_global_key() -> str:
    return "news:hot:global"


def news_hot_category_key(category_id: int) -> str:
    return f"news:hot:{category_id}"


def ai_session_state_key(session_id: str) -> str:
    return f"ai:session:state:{session_id}"


def ai_session_index_key() -> str:
    return "ai:session:index"

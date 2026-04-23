from datetime import datetime

from schemas.ai import AiChatHistoryMessage, AiChatMessage, AiSourceItem
from services.query_analysis_service import QueryAnalysis


PROMPT_VERSION = "news-assistant-v9-session-memory"
MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_CHARS = 1500
MAX_QUESTION_CHARS = 1500


MODE_CONFIG = {
    "brief": {
        "label": "快速总结",
        "instruction": "先给出结论，再补充 3 到 5 条最重要的信息点，避免空泛表述。",
    },
    "timeline": {
        "label": "事件梳理",
        "instruction": "按时间线或发展脉络组织回答，突出关键节点、转折和后续变化。",
    },
    "compare": {
        "label": "对比分析",
        "instruction": "突出不同观点、共性、差异和影响，适合做结构化比较。",
    },
}


TIME_RANGE_CONFIG = {
    "all": {
        "label": "不限时间",
        "instruction": "时间范围不做限制，但优先引用最相关的新闻证据。",
    },
    "24h": {
        "label": "近 24 小时",
        "instruction": "优先讨论最近 24 小时的变化，避免混入过旧信息。",
    },
    "7d": {
        "label": "近 7 天",
        "instruction": "优先讨论最近 7 天的新闻与动态。",
    },
}


CATEGORY_CONFIG = {
    "general": {
        "label": "综合",
        "instruction": "主题不做限制，优先围绕问题最相关的新闻内容回答。",
    },
    "technology": {
        "label": "科技",
        "instruction": "尽量从科技行业、产品、模型、平台和技术动态角度回答。",
    },
    "finance": {
        "label": "财经",
        "instruction": "尽量从市场、公司、产业和商业影响角度回答。",
    },
    "international": {
        "label": "国际",
        "instruction": "尽量从国际局势、跨国事件和全球影响角度回答。",
    },
}


def _normalize_text(content: str, max_chars: int) -> str:
    normalized = " ".join((content or "").split())
    return normalized[:max_chars].strip()


def trim_history(history: list[AiChatHistoryMessage]) -> list[AiChatHistoryMessage]:
    trimmed_items: list[AiChatHistoryMessage] = []
    remaining_chars = MAX_HISTORY_CHARS

    for item in reversed(history[-MAX_HISTORY_MESSAGES:]):
        if remaining_chars <= 0:
            break

        content = _normalize_text(item.content, remaining_chars)
        if not content:
            continue

        trimmed_items.append(AiChatHistoryMessage(role=item.role, content=content))
        remaining_chars -= len(content)

    return list(reversed(trimmed_items))


def build_system_prompt() -> str:
    return (
        "你是 NewsCopilot 的新闻助手。"
        "你只能基于我提供的新闻证据回答，不要伪造来源，也不要编造你没有看到的事实。"
        "如果给出的来源里同时包含本地新闻和 Web 搜索结果，要先总结共识，再说明补充信息。"
        "如果证据不足，必须明确说明不确定。"
        "请使用简洁、专业、适合新闻分析的中文回答。"
        "如果引用具体事实或判断，尽量在句末附上对应来源编号，例如 [1] 或 [1][2]。"
    )


def build_memory_block(memory_summary: str) -> str:
    normalized = _normalize_text(memory_summary, 1200)
    if not normalized:
        return ""
    return (
        "以下是当前会话的记忆摘要，只用于延续多轮上下文，不可替代新闻证据：\n"
        f"{normalized}"
    )


def _format_source_time(value: datetime | None) -> str:
    if not value:
        return "未知时间"
    return value.strftime("%Y-%m-%d %H:%M")


def _format_source_origin(source: AiSourceItem) -> str:
    if source.source_type == "local":
        return "本地新闻库"
    if source.domain:
        return f"Web 搜索 / {source.domain}"
    return "Web 搜索"


def build_sources_block(sources: list[AiSourceItem]) -> str:
    lines = ["以下是你必须依赖的新闻证据："]
    for index, source in enumerate(sources, start=1):
        lines.extend(
            [
                f"[{index}] 来源类型：{_format_source_origin(source)}",
                f"[{index}] 标题：{source.title}",
                f"[{index}] 发布时间：{_format_source_time(source.publish_time)}",
                f"[{index}] 证据摘要：{source.snippet}",
            ]
        )
        if source.url:
            lines.append(f"[{index}] 链接：{source.url}")
    return "\n".join(lines)


def build_query_analysis_block(query_analysis: QueryAnalysis | None) -> str:
    if not query_analysis:
        return ""

    intent_label_map = {
        "fact": "事实问答",
        "summary": "总结概览",
        "timeline": "事件梳理",
        "compare": "对比分析",
    }
    freshness_label_map = {
        "low": "低",
        "medium": "中",
        "high": "高",
    }
    scope_label_map = {
        "local": "本地优先",
        "hybrid": "本地+Web",
        "web": "Web 优先",
    }

    lines = [
        "问题分析：",
        f"- 意图：{intent_label_map.get(query_analysis.intent, query_analysis.intent)}",
        f"- 时效性需求：{freshness_label_map.get(query_analysis.freshness_need, query_analysis.freshness_need)}",
        f"- 范围偏好：{scope_label_map.get(query_analysis.scope_preference, query_analysis.scope_preference)}",
        f"- 分析说明：{query_analysis.reason}",
    ]
    if query_analysis.keyword_hints:
        lines.append(f"- 关键词提示：{'、'.join(query_analysis.keyword_hints)}")
    return "\n".join(lines)


def build_user_prompt(
    question: str,
    mode: str,
    time_range: str,
    category: str,
    sources: list[AiSourceItem],
    query_analysis: QueryAnalysis | None = None,
) -> str:
    mode_config = MODE_CONFIG.get(mode, MODE_CONFIG["brief"])
    time_range_config = TIME_RANGE_CONFIG.get(time_range, TIME_RANGE_CONFIG["all"])
    category_config = CATEGORY_CONFIG.get(category, CATEGORY_CONFIG["general"])
    normalized_question = _normalize_text(question, MAX_QUESTION_CHARS)

    return "\n".join(
        [
            "请基于当前对话上下文，以新闻助手的身份回答下列问题。",
            f"回答模式：{mode_config['label']}",
            f"模式要求：{mode_config['instruction']}",
            f"时间范围：{time_range_config['label']}",
            f"时间要求：{time_range_config['instruction']}",
            f"关注主题：{category_config['label']}",
            f"主题要求：{category_config['instruction']}",
            "回答约束：只能使用我提供的新闻证据；如果证据不足，要明确说明；不要编造时间、来源和数字。",
            "输出要求：先给出结论，再展开关键点；如涉及事实引用，请尽量在句末标注 [1]、[2] 这样的来源编号。",
            build_query_analysis_block(query_analysis),
            build_sources_block(sources),
            f"用户问题：{normalized_question}",
        ]
    )


def build_chat_messages(
    question: str,
    history: list[AiChatHistoryMessage],
    mode: str,
    time_range: str,
    category: str,
    sources: list[AiSourceItem],
    query_analysis: QueryAnalysis | None = None,
    memory_summary: str = "",
) -> list[AiChatMessage]:
    messages = [AiChatMessage(role="system", content=build_system_prompt())]
    memory_block = build_memory_block(memory_summary)
    if memory_block:
        messages.append(AiChatMessage(role="system", content=memory_block))

    for item in trim_history(history):
        messages.append(AiChatMessage(role=item.role, content=item.content))

    messages.append(
        AiChatMessage(
            role="user",
            content=build_user_prompt(
                question=question,
                mode=mode,
                time_range=time_range,
                category=category,
                sources=sources,
                query_analysis=query_analysis,
            ),
        )
    )
    return messages

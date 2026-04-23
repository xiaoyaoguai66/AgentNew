from schemas.ai import AiSourceItem


def get_runtime_status() -> dict:
    return {
        "responseFormatterEnabled": True,
        "responseFormatterStrategy": "evidence-aware-followups",
    }


def format_reply(reply: str) -> str:
    lines = [line.rstrip() for line in (reply or "").replace("\r\n", "\n").split("\n")]
    normalized_lines: list[str] = []
    previous_blank = False

    for line in lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        normalized_lines.append(line)
        previous_blank = is_blank

    return "\n".join(normalized_lines).strip()


def build_follow_up_suggestions(
    question: str,
    category: str,
    retrieval_plan: str,
    evidence_level: str,
    sources: list[AiSourceItem],
) -> list[str]:
    suggestions: list[str] = []

    if evidence_level in {"none", "weak"}:
        suggestions.append("只看近24小时，再重新梳理一次这个问题")
        suggestions.append("只基于本地新闻库，重新总结一次")

    if retrieval_plan != "web-first":
        suggestions.append("补充最新Web来源，再对这个问题更新一次")
    if retrieval_plan != "local-first":
        suggestions.append("只基于当前项目里的新闻，再给我一个站内版本")

    if category == "technology":
        suggestions.append("把这件事对大模型行业的影响单独展开说一下")
    elif category == "finance":
        suggestions.append("把这件事对公司和市场的影响单独展开说一下")
    elif category == "international":
        suggestions.append("把这件事对国际局势的影响单独展开说一下")

    if len(sources) >= 2:
        first_title = sources[0].title.strip()
        second_title = sources[1].title.strip()
        if first_title and second_title:
            suggestions.append(f"把《{first_title}》和《{second_title}》单独做一次对比")

    unique_suggestions: list[str] = []
    lowered_question = (question or "").strip()
    for item in suggestions:
        if not item or item in unique_suggestions or item == lowered_question:
            continue
        unique_suggestions.append(item)
    return unique_suggestions[:3]

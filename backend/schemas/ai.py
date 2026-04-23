from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AiChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AiChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AiChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[AiChatHistoryMessage] = Field(default_factory=list)
    mode: Literal["brief", "timeline", "compare"] = "brief"
    time_range: Literal["all", "24h", "7d"] = Field(default="all", alias="timeRange")
    category: Literal["general", "technology", "finance", "international"] = "general"
    session_id: str | None = Field(default=None, alias="sessionId")
    memory_summary: str = Field(default="", alias="memorySummary")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
    )


class AiSourceItem(BaseModel):
    source_type: Literal["local", "web"] = Field(alias="sourceType")
    news_id: int | None = Field(default=None, alias="newsId")
    title: str
    snippet: str
    url: str | None = None
    domain: str | None = None
    category_id: int | None = Field(default=None, alias="categoryId")
    publish_time: datetime | None = Field(default=None, alias="publishTime")
    retrieval_tags: list[str] = Field(default_factory=list, alias="retrievalTags")
    score: float = Field(default=0.0, ge=0.0)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiWorkflowTraceItem(BaseModel):
    step_index: int = Field(alias="stepIndex")
    node: str
    status: Literal["completed", "guarded", "fallback"]
    detail: str
    duration_ms: int = Field(alias="durationMs")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiChatResponse(BaseModel):
    reply: str
    model: str
    prompt_version: str = Field(alias="promptVersion")
    trace_id: str = Field(default="", alias="traceId")
    run_id: str = Field(default="", alias="runId")
    workflow_summary: str = Field(default="", alias="workflowSummary")
    strategy: str
    retrieval_plan: Literal["local-first", "hybrid", "web-first"] = Field(alias="retrievalPlan")
    planner_reason: str = Field(alias="plannerReason")
    query_intent: Literal["fact", "summary", "timeline", "compare"] = Field(default="fact", alias="queryIntent")
    freshness_need: Literal["low", "medium", "high"] = Field(default="low", alias="freshnessNeed")
    scope_preference: Literal["local", "hybrid", "web"] = Field(default="hybrid", alias="scopePreference")
    analysis_reason: str = Field(default="", alias="analysisReason")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verification_status: Literal["accepted", "guarded", "refused"] = Field(default="accepted", alias="verificationStatus")
    verification_reason: str = Field(default="", alias="verificationReason")
    evidence_level: Literal["none", "weak", "moderate", "strong"] = Field(default="none", alias="evidenceLevel")
    guardrail_applied: bool = Field(default=False, alias="guardrailApplied")
    follow_up_suggestions: list[str] = Field(default_factory=list, alias="followUpSuggestions")
    workflow_trace: list[AiWorkflowTraceItem] = Field(default_factory=list, alias="workflowTrace")
    sources: list[AiSourceItem] = Field(default_factory=list)
    retrieval_enabled: bool = Field(default=False, alias="retrievalEnabled")
    web_search_enabled: bool = Field(default=False, alias="webSearchEnabled")
    session_id: str = Field(default="", alias="sessionId")
    memory_enabled: bool = Field(default=False, alias="memoryEnabled")
    memory_summary: str = Field(default="", alias="memorySummary")
    memory_message_count: int = Field(default=0, alias="memoryMessageCount")
    memory_updated_at: str = Field(default="", alias="memoryUpdatedAt")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiSessionStateResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    title: str = "新对话"
    preview: str = ""
    summary: str = ""
    message_count: int = Field(default=0, alias="messageCount")
    updated_at: str = Field(default="", alias="updatedAt")
    recent_messages: list[AiChatHistoryMessage] = Field(default_factory=list, alias="recentMessages")
    memory_enabled: bool = Field(default=True, alias="memoryEnabled")
    backend: str = "redis-session-memory"

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiSessionListItem(BaseModel):
    session_id: str = Field(alias="sessionId")
    title: str = "新对话"
    preview: str = ""
    message_count: int = Field(default=0, alias="messageCount")
    updated_at: str = Field(default="", alias="updatedAt")
    active: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiSessionDeleteResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    deleted: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiIndexChunkPreviewItem(BaseModel):
    chunk_id: str = Field(alias="chunkId")
    chunk_index: int = Field(alias="chunkIndex")
    snippet: str
    text: str
    char_count: int = Field(alias="charCount")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiIndexPreviewResponse(BaseModel):
    news_id: int = Field(alias="newsId")
    title: str
    chunk_count: int = Field(alias="chunkCount")
    chunks: list[AiIndexChunkPreviewItem] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiIndexSyncRequest(BaseModel):
    news_ids: list[int] = Field(default_factory=list, alias="newsIds")
    limit: int = Field(default=20, ge=1, le=100)
    dry_run: bool = Field(default=False, alias="dryRun")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiIndexSyncResponse(BaseModel):
    dry_run: bool = Field(alias="dryRun")
    indexed_news_count: int = Field(alias="indexedNewsCount")
    chunk_count: int = Field(alias="chunkCount")
    collection: str
    vector_size: int | None = Field(default=None, alias="vectorSize")
    status: str
    upserted_points: int | None = Field(default=None, alias="upsertedPoints")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiWorkflowGraphNode(BaseModel):
    id: str
    label: str
    kind: Literal["start", "end", "node"]


class AiWorkflowGraphEdge(BaseModel):
    source: str
    target: str
    conditional: bool = False


class AiWorkflowGraphResponse(BaseModel):
    engine: str
    style: str
    graph_visualization_ready: bool = Field(alias="graphVisualizationReady")
    nodes: list[AiWorkflowGraphNode] = Field(default_factory=list)
    edges: list[AiWorkflowGraphEdge] = Field(default_factory=list)
    mermaid: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiEvalCase(BaseModel):
    case_id: str = Field(alias="caseId")
    title: str
    question: str
    mode: Literal["brief", "timeline", "compare"] = "brief"
    time_range: Literal["all", "24h", "7d"] = Field(default="all", alias="timeRange")
    category: Literal["general", "technology", "finance", "international"] = "general"
    expected_plan: Literal["local-first", "hybrid", "web-first"] = Field(alias="expectedPlan")
    expected_intent: Literal["fact", "summary", "timeline", "compare"] = Field(alias="expectedIntent")
    expected_freshness: Literal["low", "medium", "high"] = Field(alias="expectedFreshness")
    expected_scope: Literal["local", "hybrid", "web"] = Field(alias="expectedScope")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiEvalRunRequest(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    case_ids: list[str] = Field(default_factory=list, alias="caseIds")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiEvalCaseResult(BaseModel):
    case_id: str = Field(alias="caseId")
    title: str
    passed: bool
    actual_plan: str = Field(alias="actualPlan")
    expected_plan: str = Field(alias="expectedPlan")
    actual_intent: str = Field(alias="actualIntent")
    expected_intent: str = Field(alias="expectedIntent")
    actual_freshness: str = Field(alias="actualFreshness")
    expected_freshness: str = Field(alias="expectedFreshness")
    actual_scope: str = Field(alias="actualScope")
    expected_scope: str = Field(alias="expectedScope")
    planner_reason: str = Field(alias="plannerReason")
    analysis_reason: str = Field(alias="analysisReason")
    mismatches: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiEvalRunResponse(BaseModel):
    run_id: str = Field(alias="runId")
    total_count: int = Field(alias="totalCount")
    passed_count: int = Field(alias="passedCount")
    web_enabled: bool = Field(alias="webEnabled")
    planner_accuracy: float = Field(alias="plannerAccuracy")
    intent_accuracy: float = Field(alias="intentAccuracy")
    freshness_accuracy: float = Field(alias="freshnessAccuracy")
    scope_accuracy: float = Field(alias="scopeAccuracy")
    results: list[AiEvalCaseResult] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiEvalRunLogItem(BaseModel):
    run_id: str = Field(alias="runId")
    recorded_at: str = Field(alias="recordedAt")
    total_count: int = Field(alias="totalCount")
    passed_count: int = Field(alias="passedCount")
    planner_accuracy: float = Field(alias="plannerAccuracy")
    intent_accuracy: float = Field(alias="intentAccuracy")
    freshness_accuracy: float = Field(alias="freshnessAccuracy")
    scope_accuracy: float = Field(alias="scopeAccuracy")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiEvalFailureItem(BaseModel):
    run_id: str = Field(alias="runId")
    recorded_at: str = Field(alias="recordedAt")
    case_id: str = Field(alias="caseId")
    title: str
    mismatches: list[str] = Field(default_factory=list)
    expected_plan: str = Field(alias="expectedPlan")
    actual_plan: str = Field(alias="actualPlan")
    expected_intent: str = Field(alias="expectedIntent")
    actual_intent: str = Field(alias="actualIntent")
    expected_freshness: str = Field(alias="expectedFreshness")
    actual_freshness: str = Field(alias="actualFreshness")
    expected_scope: str = Field(alias="expectedScope")
    actual_scope: str = Field(alias="actualScope")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiLangsmithEvalStatusResponse(BaseModel):
    langsmith_ready: bool = Field(alias="langsmithReady")
    langsmith_configured: bool = Field(alias="langsmithConfigured")
    dataset_upload_ready: bool = Field(alias="datasetUploadReady")
    project: str
    default_dataset_name: str = Field(alias="defaultDatasetName")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiLangsmithEvalExportExample(BaseModel):
    inputs: dict
    outputs: dict
    metadata: dict = Field(default_factory=dict)


class AiLangsmithEvalExportResponse(BaseModel):
    dataset_name: str = Field(alias="datasetName")
    example_count: int = Field(alias="exampleCount")
    examples: list[AiLangsmithEvalExportExample] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiLangsmithEvalSyncRequest(BaseModel):
    dataset_name: str | None = Field(default=None, alias="datasetName")
    limit: int = Field(default=20, ge=1, le=100)
    case_ids: list[str] = Field(default_factory=list, alias="caseIds")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiLangsmithEvalSyncResponse(BaseModel):
    synced: bool
    dataset_name: str = Field(alias="datasetName")
    example_count: int = Field(alias="exampleCount")
    dataset_id: str | None = Field(default=None, alias="datasetId")
    note: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiResponseEvalCase(BaseModel):
    case_id: str = Field(alias="caseId")
    title: str
    question: str
    mode: Literal["brief", "timeline", "compare"] = "brief"
    time_range: Literal["all", "24h", "7d"] = Field(default="all", alias="timeRange")
    category: Literal["general", "technology", "finance", "international"] = "general"
    allowed_statuses: list[Literal["accepted", "guarded", "refused"]] = Field(alias="allowedStatuses")
    min_sources: int = Field(default=0, alias="minSources")
    max_sources: int = Field(default=10, alias="maxSources")
    require_follow_ups: bool = Field(default=True, alias="requireFollowUps")
    require_workflow_trace: bool = Field(default=True, alias="requireWorkflowTrace")
    require_non_empty_reply: bool = Field(default=True, alias="requireNonEmptyReply")
    note: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiResponseEvalRunRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=50)
    case_ids: list[str] = Field(default_factory=list, alias="caseIds")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiResponseEvalCaseResult(BaseModel):
    case_id: str = Field(alias="caseId")
    title: str
    passed: bool
    actual_status: str = Field(alias="actualStatus")
    allowed_statuses: list[str] = Field(default_factory=list, alias="allowedStatuses")
    source_count: int = Field(alias="sourceCount")
    follow_up_count: int = Field(alias="followUpCount")
    workflow_trace_count: int = Field(alias="workflowTraceCount")
    mismatches: list[str] = Field(default_factory=list)
    note: str = ""

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiResponseEvalRunResponse(BaseModel):
    run_id: str = Field(alias="runId")
    total_count: int = Field(alias="totalCount")
    passed_count: int = Field(alias="passedCount")
    status_accuracy: float = Field(alias="statusAccuracy")
    contract_accuracy: float = Field(alias="contractAccuracy")
    results: list[AiResponseEvalCaseResult] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiResponseEvalRunLogItem(BaseModel):
    run_id: str = Field(alias="runId")
    recorded_at: str = Field(alias="recordedAt")
    total_count: int = Field(alias="totalCount")
    passed_count: int = Field(alias="passedCount")
    status_accuracy: float = Field(alias="statusAccuracy")
    contract_accuracy: float = Field(alias="contractAccuracy")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class AiResponseEvalFailureItem(BaseModel):
    run_id: str = Field(alias="runId")
    recorded_at: str = Field(alias="recordedAt")
    case_id: str = Field(alias="caseId")
    title: str
    actual_status: str = Field(alias="actualStatus")
    allowed_statuses: list[str] = Field(default_factory=list, alias="allowedStatuses")
    source_count: int = Field(alias="sourceCount")
    follow_up_count: int = Field(alias="followUpCount")
    workflow_trace_count: int = Field(alias="workflowTraceCount")
    mismatches: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

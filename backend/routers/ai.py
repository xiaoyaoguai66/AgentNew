from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from schemas.ai import (
    AiChatRequest,
    AiEvalCase,
    AiEvalFailureItem,
    AiEvalRunLogItem,
    AiEvalRunRequest,
    AiEvalRunResponse,
    AiIndexPreviewResponse,
    AiIndexSyncRequest,
    AiIndexSyncResponse,
    AiLangsmithEvalExportResponse,
    AiLangsmithEvalStatusResponse,
    AiLangsmithEvalSyncRequest,
    AiLangsmithEvalSyncResponse,
    AiResponseEvalCase,
    AiResponseEvalFailureItem,
    AiResponseEvalRunLogItem,
    AiResponseEvalRunRequest,
    AiResponseEvalRunResponse,
    AiSessionDeleteResponse,
    AiSessionListItem,
    AiSessionStateResponse,
    AiWorkflowGraphResponse,
)
from services import (
    agent_eval_artifact_service,
    agent_evaluation_service,
    agent_memory_service,
    agent_observability_service,
    agent_response_evaluation_service,
    agent_workflow_graph_service,
    langsmith_evaluation_service,
    news_agent_service,
    vector_index_pipeline_service,
)
from utils.response import success_response


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status")
async def get_status():
    status_payload = news_agent_service.get_runtime_status()
    return success_response(message="AI status loaded.", data=status_payload)


@router.post("/chat")
async def chat(
    data: AiChatRequest,
    db: AsyncSession = Depends(get_db),
):
    response = await news_agent_service.chat(db, data)
    return success_response(message="AI reply generated.", data=response)


@router.post("/session/start")
async def start_session():
    payload = await agent_memory_service.create_session()
    return success_response(
        message="AI session started.",
        data=AiSessionStateResponse.model_validate(
            agent_memory_service.format_session_response(payload)
        ),
    )


@router.get("/sessions")
async def list_sessions(limit: int = 20, active_session_id: str = ""):
    payload = await agent_memory_service.list_sessions(limit=limit)
    return success_response(
        message="AI sessions loaded.",
        data=[
            AiSessionListItem.model_validate(
                {
                    **item,
                    "active": item.get("sessionId") == active_session_id,
                }
            )
            for item in payload
        ],
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    payload = await agent_memory_service.get_session(session_id)
    if payload is None:
        payload = await agent_memory_service.create_session(session_id)
    return success_response(
        message="AI session loaded.",
        data=AiSessionStateResponse.model_validate(
            agent_memory_service.format_session_response(payload)
        ),
    )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    deleted = await agent_memory_service.clear_session(session_id)
    return success_response(
        message="AI session cleared.",
        data=AiSessionDeleteResponse.model_validate(
            {
                "sessionId": session_id,
                "deleted": deleted,
            }
        ),
    )


@router.get("/runs/recent")
async def get_recent_runs(limit: int = 10):
    runs = agent_observability_service.read_recent_runs(limit=limit)
    return success_response(message="AI runs loaded.", data=runs)


@router.get("/workflow/graph")
async def get_workflow_graph():
    payload = agent_workflow_graph_service.get_workflow_graph()
    return success_response(
        message="Workflow graph loaded.",
        data=AiWorkflowGraphResponse.model_validate(payload),
    )


@router.get("/eval/dataset")
async def get_eval_dataset():
    cases = agent_evaluation_service.load_eval_dataset()
    return success_response(
        message="Evaluation dataset loaded.",
        data=[AiEvalCase.model_validate(item) for item in cases],
    )


@router.post("/eval/run")
async def run_eval(data: AiEvalRunRequest):
    payload = agent_evaluation_service.run_eval(limit=data.limit, case_ids=data.case_ids)
    return success_response(
        message="Evaluation finished.",
        data=AiEvalRunResponse.model_validate(payload),
    )


@router.get("/eval/runs/recent")
async def get_recent_eval_runs(limit: int = 10):
    payload = agent_eval_artifact_service.read_recent_eval_runs(limit=limit)
    return success_response(
        message="Evaluation runs loaded.",
        data=[AiEvalRunLogItem.model_validate(item) for item in payload],
    )


@router.get("/eval/failures/recent")
async def get_recent_eval_failures(limit: int = 10):
    payload = agent_eval_artifact_service.read_recent_failure_cases(limit=limit)
    return success_response(
        message="Evaluation failures loaded.",
        data=[AiEvalFailureItem.model_validate(item) for item in payload],
    )


@router.get("/eval/langsmith/status")
async def get_langsmith_eval_status():
    payload = langsmith_evaluation_service.get_runtime_status()
    return success_response(
        message="LangSmith evaluation status loaded.",
        data=AiLangsmithEvalStatusResponse.model_validate(payload),
    )


@router.get("/eval/langsmith/export")
async def export_langsmith_eval(limit: int = 20):
    payload = langsmith_evaluation_service.build_export_payload(limit=limit)
    return success_response(
        message="LangSmith export payload loaded.",
        data=AiLangsmithEvalExportResponse.model_validate(payload),
    )


@router.post("/eval/langsmith/sync")
async def sync_langsmith_eval(data: AiLangsmithEvalSyncRequest):
    payload = langsmith_evaluation_service.sync_dataset(
        limit=data.limit,
        case_ids=data.case_ids,
        dataset_name=data.dataset_name,
    )
    return success_response(
        message="LangSmith evaluation dataset sync finished.",
        data=AiLangsmithEvalSyncResponse.model_validate(payload),
    )


@router.get("/eval/response/dataset")
async def get_response_eval_dataset():
    payload = agent_response_evaluation_service.load_response_eval_dataset()
    return success_response(
        message="Response evaluation dataset loaded.",
        data=[AiResponseEvalCase.model_validate(item) for item in payload],
    )


@router.post("/eval/response/run")
async def run_response_eval(
    data: AiResponseEvalRunRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = await agent_response_evaluation_service.run_response_eval(
        db,
        limit=data.limit,
        case_ids=data.case_ids,
    )
    return success_response(
        message="Response evaluation finished.",
        data=AiResponseEvalRunResponse.model_validate(payload),
    )


@router.get("/eval/response/runs/recent")
async def get_recent_response_eval_runs(limit: int = 10):
    payload = agent_eval_artifact_service.read_recent_response_eval_runs(limit=limit)
    return success_response(
        message="Response evaluation runs loaded.",
        data=[AiResponseEvalRunLogItem.model_validate(item) for item in payload],
    )


@router.get("/eval/response/failures/recent")
async def get_recent_response_eval_failures(limit: int = 10):
    payload = agent_eval_artifact_service.read_recent_response_failure_cases(limit=limit)
    return success_response(
        message="Response evaluation failures loaded.",
        data=[AiResponseEvalFailureItem.model_validate(item) for item in payload],
    )


@router.get("/index/status")
async def get_index_status():
    status_payload = vector_index_pipeline_service.get_runtime_status()
    return success_response(message="Vector index status loaded.", data=status_payload)


@router.get("/index/preview/{news_id}")
async def preview_news_index(
    news_id: int,
    db: AsyncSession = Depends(get_db),
):
    response = await vector_index_pipeline_service.preview_news_chunks(db, news_id)
    return success_response(
        message="News chunks preview loaded.",
        data=AiIndexPreviewResponse.model_validate(response),
    )


@router.post("/index/sync")
async def sync_news_index(
    data: AiIndexSyncRequest,
    db: AsyncSession = Depends(get_db),
):
    response = await vector_index_pipeline_service.sync_news_index(
        db,
        news_ids=data.news_ids,
        limit=data.limit,
        dry_run=data.dry_run,
    )
    return success_response(
        message="Vector index sync finished.",
        data=AiIndexSyncResponse.model_validate(response),
    )

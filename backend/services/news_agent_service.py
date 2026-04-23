from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from schemas.ai import AiChatRequest, AiChatResponse
from services import agent_memory_service, agent_workflow_service, langgraph_agent_service


def _get_engine():
    settings = get_settings()
    if settings.agent_workflow_engine == "legacy":
        return agent_workflow_service
    return langgraph_agent_service


def get_runtime_status() -> dict:
    return {
        **_get_engine().get_runtime_status(),
        **agent_memory_service.get_runtime_status(),
    }


async def chat(db: AsyncSession, data: AiChatRequest) -> AiChatResponse:
    prepared_request, _ = await agent_memory_service.prepare_request(data)
    response = await _get_engine().chat(db, prepared_request)
    return await agent_memory_service.persist_response(prepared_request, response)

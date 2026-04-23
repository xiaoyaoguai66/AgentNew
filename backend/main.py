import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from routers import ai, favorite, history, news, users
from services import qdrant_index_service
from tasks.news_metrics import flush_news_view_deltas_once
from utils.exception_handlers import register_exception_handlers


settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI()
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "NewsCopilot API",
        "status": "ok",
        "workflowEngine": settings.agent_workflow_engine,
    }


@app.get("/health")
async def health():
    return {
        "service": "NewsCopilot API",
        "status": "healthy",
        "redisConfigured": bool(settings.redis_url),
        "vectorEnabled": settings.enable_vector_retrieval,
        "workflowEngine": settings.agent_workflow_engine,
    }


@app.on_event("startup")
async def startup_news_metrics_worker():
    stop_event = asyncio.Event()
    app.state.news_metrics_stop_event = stop_event

    async def run_worker():
        while not stop_event.is_set():
            try:
                await flush_news_view_deltas_once()
            except Exception:
                logger.exception("news view flush worker failed unexpectedly")

            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=settings.view_flush_interval_seconds,
                )
            except TimeoutError:
                continue

    app.state.news_metrics_task = asyncio.create_task(run_worker())


@app.on_event("shutdown")
async def shutdown_news_metrics_worker():
    stop_event = getattr(app.state, "news_metrics_stop_event", None)
    worker_task = getattr(app.state, "news_metrics_task", None)

    if stop_event is not None:
        stop_event.set()
    if worker_task is not None:
        await worker_task

    # Release the local Qdrant file lock on shutdown so the next run can reuse
    # the same storage directory cleanly.
    qdrant_index_service.close_client()


app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai.router)


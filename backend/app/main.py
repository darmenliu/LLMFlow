import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.taskmanager.task_manager_singleton import init_task_manager
from app.db.session import get_session


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    # 初始化任务管理器
    db = next(get_session())
    init_task_manager(
        db_session=db,
        finetune_image=settings.FINETUNE_IMAGE,
        namespace=settings.FINETUNE_NAMESPACE,
        max_concurrent_tasks=settings.MAX_CONCURRENT_TASKS,
        max_tasks_per_user=settings.MAX_TASKS_PER_USER
    )

def init_app():
    # 其他初始化代码...
    pass

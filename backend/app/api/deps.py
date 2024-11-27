from collections.abc import Generator
from typing import Annotated
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.core.taskmanager.finetune_task_manager import FinetuneTaskManager
from app.core.finetune.finetune_impl_k8s_job import K8sFinetuneService
from app.core.kubeclient.finetune_jobs import FinetuneJobClient
from app.db.session import get_session

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


@lru_cache()
def get_task_manager(
    session = Depends(get_session)
) -> FinetuneTaskManager:
    """获取任务管理器单例"""
    # 创建K8s任务客户端
    job_client = FinetuneJobClient(
        config_file=None,  # 使用默认配置
        finetune_image="your-finetune-image:latest",
        default_namespace="finetune"
    )
    
    # 创建微调服务
    finetune_service = K8sFinetuneService(
        finetune_job_client=job_client,
        db_session=session,
        namespace="finetune"
    )
    
    # 创建任务管理器
    return FinetuneTaskManager(
        finetune_service=finetune_service,
        max_concurrent_tasks=5,
        max_tasks_per_user=3
    )

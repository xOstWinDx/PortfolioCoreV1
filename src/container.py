from dependency_injector import containers, providers
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.application.usecases.add_project import AddNewProjectUseCase
from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.config import CONFIG
from src.infrastructure.clients.redis import RedisClient
from src.infrastructure.services.auth import AuthService
from src.infrastructure.uow.project import ProjectsUnitOfWork


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_async_engine, url=CONFIG.DEV_DATABASE_URL)

    session_factory = providers.Factory(
        async_sessionmaker, bind=engine, expire_on_commit=False
    )

    projects_uow = providers.Factory(
        ProjectsUnitOfWork, session_factory=session_factory
    )

    create_project_use_case = providers.Factory(
        AddNewProjectUseCase, project_uow=projects_uow
    )

    auth_service = providers.Factory(AuthService)

    redis = providers.Factory(
        Redis.from_url, url=CONFIG.DEV_REDIS_URL, decode_responses=True
    )

    cache_client = providers.Factory(RedisClient, redis=redis)

    login_use_case = providers.Factory(
        LoginUseCase, auth=auth_service, cache=cache_client
    )

    update_token_use_case = providers.Factory(
        UpdateTokenUseCase, auth_service=auth_service, cache_client=cache_client
    )

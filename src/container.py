from dependency_injector import containers, providers
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.application.usecases.add_project import AddNewProjectUseCase
from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.config import CONFIG
from src.infrastructure.services.auth import AuthService
from src.infrastructure.unit_of_work import UnitOfWork


# TODO: добавить конфиг как синглтон сюда, а так-же уточнить роль ЮОВ


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_async_engine, url=CONFIG.DEV_DATABASE_URL)

    session_factory = providers.Singleton(
        async_sessionmaker, bind=engine, expire_on_commit=False
    )

    auth_service = providers.Factory(AuthService)

    redis = providers.Factory(
        Redis.from_url, url=CONFIG.DEV_REDIS_URL, decode_responses=True
    )

    uow = providers.Factory(
        UnitOfWork,
        session_factory=session_factory,
        redis_client=redis,
    )

    login_use_case = providers.Factory(
        LoginUseCase, uow_factory=uow, auth_service_factory=auth_service
    )

    update_token_use_case = providers.Factory(
        UpdateTokenUseCase, auth_service=auth_service, uow=uow
    )

    create_project_use_case = providers.Factory(AddNewProjectUseCase, uow=uow)


container = Container()

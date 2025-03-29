from dependency_injector import containers, providers
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.application.authorize import AuthDecorator
from src.application.usecases.add_project import AddNewProjectUseCase
from src.application.usecases.login import LoginUseCase
from src.application.usecases.register_user import RegisterUserUseCase
from src.application.usecases.update_token import UpdateCredentialsUseCase
from src.config import CONFIG
from src.domain.entities.user import RolesEnum
from src.infrastructure.credentials import JwtCredentials
from src.infrastructure.services.auth import JwtAuthService
from src.infrastructure.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    engine = providers.Singleton(create_async_engine, url=CONFIG.DEV_DATABASE_URL)

    session_factory = providers.Singleton(
        async_sessionmaker, bind=engine, expire_on_commit=False
    )

    auth_service = providers.Factory(JwtAuthService)

    redis = providers.Factory(
        Redis.from_url, url=CONFIG.DEV_REDIS_URL, decode_responses=True
    )

    admin_auth = providers.Singleton(AuthDecorator, required_role=RolesEnum.ADMIN)

    user_auth = providers.Singleton(AuthDecorator, required_role=RolesEnum.USER)

    guest_auth = providers.Singleton(AuthDecorator, required_role=RolesEnum.GUEST)

    uow = providers.Factory(
        UnitOfWork,
        session_factory=session_factory,
        redis_client=redis,
    )

    register_use_case = providers.Factory(
        RegisterUserUseCase, uow=uow, auth_service=auth_service, _authorize=guest_auth
    )

    login_use_case = providers.Factory(
        LoginUseCase,
        uow_factory=uow,
        auth_service_factory=auth_service,
        _authorize=guest_auth,
    )

    update_token_use_case = providers.Factory(
        UpdateCredentialsUseCase, auth_service=auth_service, uow=uow
    )

    create_project_use_case = providers.Factory(AddNewProjectUseCase, uow=uow)

    credentials = providers.Factory(JwtCredentials, token=providers.Callable(str))


container = Container()

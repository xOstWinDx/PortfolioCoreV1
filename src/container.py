from dependency_injector import containers, providers
from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.application.authorize import UseCaseGuard
from src.application.usecases.add_project import CreateProjectUseCase
from src.application.usecases.login import LoginUseCase
from src.application.usecases.register_user import RegisterUserUseCase
from src.application.usecases.update_token import UpdateCredentialsUseCase
from src.config import CONFIG
from src.domain.entities.user import RolesEnum
from src.domain.value_objects.auth import AuthorizationContext
from src.infrastructure.credentials import JwtCredentials
from src.infrastructure.repositories.tokens import JWTRedisAuthRepository
from src.infrastructure.services.auth import JwtAuthService
from src.infrastructure.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    # region Base depends
    engine = providers.Singleton(create_async_engine, url=CONFIG.DATABASE_URL)

    session_factory = providers.Singleton(
        async_sessionmaker, bind=engine, expire_on_commit=False
    )
    redis_pool = providers.Singleton(
        ConnectionPool.from_url,
        url=CONFIG.DEV_REDIS_URL,
        decode_responses=True,
    )

    redis = providers.Singleton(  # Ресурс провайдер обеспечивает открытие и закрытие соединения
        Redis,
        connection_pool=redis_pool,
    )
    auth_repo = providers.Factory(JWTRedisAuthRepository, redis_client=redis)
    auth_service = providers.Factory(JwtAuthService, auth_repo=auth_repo)

    uow = providers.Factory(UnitOfWork, session_factory=session_factory)
    # endregion

    # region Credentials
    credentials = providers.Factory(
        JwtCredentials,
        authorize=providers.Callable(str),
        authenticate=providers.Callable(str),
    )

    default_context = providers.Singleton(
        AuthorizationContext,
        user_id=None,
        role=RolesEnum.GUEST,
    )
    # endregion

    # region Use cases without auth
    _register_use_case = providers.Factory(
        RegisterUserUseCase,
        uow=uow,
        auth=auth_service,
    )
    _login_use_case = providers.Factory(
        LoginUseCase,
        uow=uow,
        auth=auth_service,
    )
    _update_token_use_case = providers.Factory(
        UpdateCredentialsUseCase,
        auth=auth_service,
        uow=uow,
    )
    _create_project_use_case = providers.Factory(
        CreateProjectUseCase,
        uow=uow,
        auth=auth_service,
    )
    # endregion

    # region Use cases with auth
    register_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_register_use_case,
        uow=uow,
        default_context=default_context,
    )
    login_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_login_use_case,
        uow=uow,
        default_context=default_context,
    )
    update_token_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_update_token_use_case,
        uow=uow,
        default_context=default_context,
    )
    create_project_use_case: CreateProjectUseCase = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.ADMIN,
        auth_service=auth_service,
        use_case=_create_project_use_case,
        uow=uow,
        default_context=default_context,
    )
    # endregion


container = Container()

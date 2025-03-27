from dependency_injector import containers, providers
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.application.usecases.add_project import AddNewProjectUseCase
from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.config import CONFIG
from src.infrastructure.services.auth import AuthService
from src.infrastructure.unit_of_work import UnitOfWork


# class LoginUseCaseProvider(Provider):
#     def __init__(
#             self,
#             use_case_cls: type[LoginUseCase],
#             uow_factory: Factory[AbstractUnitOfWork],
#             auth_service_factory: Factory[AbstractAuthService],
#     ):
#         self.use_case_cls = use_case_cls
#         self.uow_factory = uow_factory
#         self.auth_service_factory = auth_service_factory
#         super().__init__()
#
#     @asynccontextmanager
#     async def _provide(self):
#         uow = self.uow_factory()
#         async with uow:
#             yield self.use_case_cls(
#                 user_repo=uow.users,
#                 token_repo=uow.tokens,
#                 auth=self.auth_service_factory(),
#             )
#
#     def __call__(self):
#         return self._provide()
#
#
# class UpdateTokenUseCaseProvider(Provider):
#     def __init__(
#             self,
#             use_case_cls: type[UpdateTokenUseCase],
#             auth_service_factory: Factory[AbstractAuthService],
#             uow_factory: Factory[AbstractUnitOfWork],
#     ):
#         self.use_case_cls = use_case_cls
#         self.auth_service_factory = auth_service_factory
#         self.uow_factory = uow_factory
#         super().__init__()
#
#     @asynccontextmanager
#     async def _provide(self):
#         async with self.uow_factory() as uow:
#             yield self.use_case_cls(
#                 auth_service=self.auth_service_factory(),
#                 token_repo=uow.tokens,
#                 users_repo=uow.users
#             )
#
#     def __call__(self):
#         return self._provide()
#
#
# class AddProjectUseCaseProvider(Provider):
#     def __init__(
#             self,
#             use_case_cls: type[AddNewProjectUseCase],
#             uow_factory: Factory[AbstractUnitOfWork],
#     ):
#         self.use_case_cls = use_case_cls
#         self.uow_factory = uow_factory
#         super().__init__()
#
#     @asynccontextmanager
#     async def _provide(self):
#         async with self.uow_factory() as uow:
#             yield self.use_case_cls(project_uow=uow.projects)
#
#     def __call__(self):
#         return self._provide()


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

import logging
from typing import TypeVar, Generic

from src.application.interfaces.credentials import Credentials
from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.usecases.abs import AbstractUseCase
from src.context import CredentialsHolder
from src.domain.entities.user import RolesEnum
from src.domain.exceptions.auth import TokenError, AccessDeniedError
from src.domain.filters.users import UserFilter
from src.domain.value_objects.auth import AuthorizationContext

logger = logging.getLogger(__name__)

U = TypeVar("U", bound=AbstractUseCase)


class UseCaseGuard(Generic[U]):
    def __init__(
        self,
        required_role: RolesEnum,
        auth_service: AbstractAuthService,
        use_case: U,
        uow: AbstractUnitOfWork,
        default_context: AuthorizationContext,
    ):
        self.required_role = required_role
        self.auth = auth_service
        self.__use_case = use_case
        self.uow = uow
        self.default_context = default_context
        self.__credentials: None | Credentials = None
        self.__creds_holder: None | CredentialsHolder = None
        self.__device_id: None | str = None

    def configure(
        self,
        *,
        credentials: Credentials,
        creds_holder: CredentialsHolder,
        device_id: str,
    ) -> None:
        self.__credentials = credentials
        self.__creds_holder = creds_holder
        self.__device_id = device_id

    async def __aenter__(self) -> tuple[U, AuthorizationContext, Credentials]:
        if (
            self.__credentials is None
            or self.__creds_holder is None
            or self.__device_id is None
        ):
            raise RuntimeError("AuthDecorator must be configured before use")
        try:
            context = await self.auth.authorize(
                credentials=self.__credentials, device_id=self.__device_id
            )
        except TokenError:
            try:
                new_credentials = await self._try_renew_creds(
                    credentials=self.__credentials
                )
                context = await self.auth.authorize(
                    credentials=new_credentials, device_id=self.__device_id
                )
                self.__creds_holder.credentials = new_credentials
            except TokenError as e:
                logger.warning("Access denied: no token found", exc_info=e)
                context = self.default_context
        message = f"Access denied: required {self.required_role.name} or higher, got {context.role.name}"
        if context.role == RolesEnum.GUEST:
            message += " (possibly due to an invalid or expired token)"
        if context.role < self.required_role:
            raise AccessDeniedError(message)
        credentials = self.__creds_holder.credentials or self.__credentials

        return self.__use_case, context, credentials

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        self.__credentials = None
        self.__creds_holder = None

    async def _try_renew_creds(self, credentials: Credentials) -> Credentials:
        user_id = self.auth.get_subject_id(credentials=credentials)
        if not user_id:
            raise TokenError("Missing user id")
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(id=user_id))
            if user is None:
                raise TokenError("User not found")
        credentials = await self.auth.renew_credentials(
            credentials=credentials,
            user=user,
            device_id=self.__device_id if self.__device_id else "*",
        )
        return credentials

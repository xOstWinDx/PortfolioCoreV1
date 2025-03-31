import logging
from inspect import signature
from typing import Callable, Awaitable, Any

from src.application.interfaces.credentials import Credentials
from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.entities.user import RolesEnum
from src.domain.exceptions.auth import TokenError
from src.domain.filters.users import UserFilter
from src.domain.value_objects.auth import AuthorizationContext

logger = logging.getLogger(__name__)


class AuthDecorator:
    def __init__(
        self,
        required_role: RolesEnum,
        auth_service: AbstractAuthService,
        use_case: Callable[..., Awaitable[Any]],
        uow: AbstractUnitOfWork,
        default_context: AuthorizationContext,
    ):
        self.required_role = required_role
        self.auth = auth_service
        self.use_case = use_case
        self.uow = uow
        self.default_context = default_context

    async def __call__(self, *args, **kwargs):  # type: ignore
        print(f"In auth decorator with {args} and {kwargs}")
        credentials: Credentials | None = kwargs.get("credentials", None)
        if credentials is None:
            raise ValueError("credentials keyword is required")
        try:
            context = await self.auth.authorize(credentials=credentials)
        except TokenError:
            try:
                context = await self._try_renew_creds(credentials=credentials)
            except TokenError:
                context = self.default_context

        message = f"Access denied: required {self.required_role} or higher, got {context.role}"
        if context.role == RolesEnum.GUEST:
            message += " (possibly due to an invalid or expired token)"
        if context.role < self.required_role:
            raise PermissionError(message)

        if "context" in signature(self.use_case).parameters:
            kwargs["context"] = context

        return await self.use_case(*args, **kwargs)

    async def _try_renew_creds(self, credentials: Credentials) -> AuthorizationContext:
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
        )
        return await self.auth.authorize(credentials=credentials)

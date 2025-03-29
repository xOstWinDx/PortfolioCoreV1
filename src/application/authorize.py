import functools
import logging
from typing import Awaitable, Callable

from src.application.interfaces.credentials import Credentials
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.user import RolesEnum

logger = logging.getLogger(__name__)


class AuthDecorator:
    def __init__(self, required_role: RolesEnum):
        self.required_role = required_role

    def __call__(
        self,
        func: Callable[[AbstractUseCase, Credentials, ...], Awaitable],  # type: ignore
    ) -> Callable[[AbstractUseCase, Credentials, ...], Awaitable]:  # type: ignore
        req_role = self.required_role

        @functools.wraps(func)
        async def wrapper(  # type: ignore
            self: AbstractUseCase, credentials: Credentials, *args, **kwargs
        ):
            context = await self.auth.authorize(credentials=credentials)
            message = (
                f"Access denied: required {req_role} or higher, got {context.role}"
            )
            if context.role == RolesEnum.GUEST:
                message += " (possibly due to an invalid or expired token)"
            if context.role < req_role:
                raise PermissionError(message)
            from inspect import signature

            if "context" in signature(func).parameters:
                kwargs["context"] = context
            return await func(self, *args, **kwargs)

        return wrapper

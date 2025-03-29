import functools
import logging
from typing import Awaitable, Callable

from src.application.interfaces.credentials import Credentials
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.user import RolesEnum

logger = logging.getLogger(__name__)


class AuthDecorator:
    """Декоратор для проверки прав доступа, требует 'credentials':keyword функции."""

    def __init__(self, required_role: RolesEnum):
        self.required_role = required_role

    def __call__(
        self,
        func: Callable[[AbstractUseCase, Credentials, ...], Awaitable],  # type: ignore
    ) -> Callable[[AbstractUseCase, Credentials, ...], Awaitable]:  # type: ignore
        req_role = self.required_role

        @functools.wraps(func)
        async def wrapper(self: AbstractUseCase, *args, **kwargs):  # type: ignore
            from inspect import signature

            if "credentials" not in signature(func).parameters:
                raise ValueError("credentials keyword is required")
            context = await self.auth.authorize(credentials=kwargs["credentials"])
            message = (
                f"Access denied: required {req_role} or higher, got {context.role}"
            )
            if context.role == RolesEnum.GUEST:
                message += " (possibly due to an invalid or expired token)"
            if context.role < req_role:
                raise PermissionError(message)

            if "context" in signature(func).parameters:
                kwargs["context"] = context
            return await func(self, *args, **kwargs)

        return wrapper

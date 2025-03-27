from datetime import datetime, UTC

from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.domain.entities.user import User
from src.domain.exceptions.auth import UserAlreadyExistsError
from src.domain.filters.users import UserFilter


# TODO: рефакторинг uow - общий для всего SQL у которого все репозитории при входе в контекст!


class RegisterUserUseCase:
    def __init__(self, uow: AbstractUnitOfWork, auth_service: AbstractAuthService):
        self.uow = uow
        self.auth_service = auth_service

    async def __call__(self, username: str, email: str, password: str) -> User:
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(email=email))
            if user is not None:
                raise UserAlreadyExistsError(email)
            user = User(
                username=username,
                email=email,
                password=self.auth_service.hash_password(password),
                id=None,
                created_at=datetime.now(UTC),
                roles=["user"],
            )
            return await uow.users.register(user)

from datetime import datetime, UTC

from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.user import User, RolesEnum
from src.domain.exceptions.auth import UserAlreadyExistsError
from src.domain.filters.users import UserFilter


class RegisterUserUseCase(AbstractUseCase):
    async def __call__(self, username: str, email: str, password: str) -> User:
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(email=email))
            if user is not None:
                raise UserAlreadyExistsError(email)
            user = User(
                username=username,
                email=email,
                password=self.auth.hash_password(password),
                id=None,
                created_at=datetime.now(UTC),
                role=RolesEnum.USER,
            )
            return await uow.users.register(user)

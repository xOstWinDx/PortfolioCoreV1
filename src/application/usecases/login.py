from src.application.interfaces.credentials import Credentials
from src.application.usecases.abs import AbstractUseCase
from src.domain.filters.users import UserFilter


class LoginUseCase(AbstractUseCase):
    async def __call__(
        self, *, credentials: Credentials, email: str, password: str
    ) -> Credentials:
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(email=email))
            return await self.auth.authenticate(
                email=email, password=password, user=user
            )

from src.application.interfaces.credentials import Credentials
from src.application.usecases.abs import AbstractUseCase
from src.domain.filters.users import UserFilter


class LoginUseCase(AbstractUseCase):
    async def __call__(
        self,
        email: str,
        password: str,
        device_id: str,
        *,
        credentials: Credentials | None = None,
    ) -> Credentials:
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(email=email))
            return await self.auth.authenticate(
                email=email, password=password, user=user, device_id=device_id
            )

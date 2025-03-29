from src.application.interfaces.credentials import Credentials
from src.application.usecases.abs import AbstractUseCase
from src.domain.exceptions.auth import SubjectNotFoundError
from src.domain.filters.users import UserFilter


class UpdateCredentialsUseCase(AbstractUseCase):
    async def __call__(self, credentials: Credentials) -> Credentials:
        flow = await self.auth.renew_credentials(credentials)
        subject_id: int = await flow.__anext__()  # type: ignore
        if isinstance(subject_id, int):
            async with self.uow as uow:
                user = await uow.users.get_user(UserFilter(id=subject_id))
                if user is None:
                    raise SubjectNotFoundError()
        return await flow.asend(user)  # type: ignore

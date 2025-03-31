from src.application.usecases.abs import AbstractUseCase


class UpdateCredentialsUseCase(AbstractUseCase):
    # async def __call__(self, *, credentials: Credentials) -> Credentials:
    #     flow = await self.auth.renew_credentials(credentials)
    #     subject_id: int = await flow.__anext__()  # type: ignore
    #     if isinstance(subject_id, int):
    #         async with self.uow as uow:
    #             user = await uow.users.get_user(UserFilter(id=subject_id))
    #             if user is None:
    #                 raise SubjectNotFoundError()
    #     return await flow.asend(user)  # type: ignore

    # ────────────────
    # TODO [31.03.2025 | Low]
    # Assigned to: stark
    # Description: Переписать
    # Steps:
    #   - Всё и так понятно
    # ────────────────
    pass

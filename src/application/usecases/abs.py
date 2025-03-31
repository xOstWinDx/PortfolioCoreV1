from abc import ABC, abstractmethod

from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork


class AbstractUseCase(ABC):
    def __init__(
        self,
        auth: AbstractAuthService,
        uow: AbstractUnitOfWork,
    ):
        self.auth = auth
        self.uow = uow

    @abstractmethod
    async def __call__(self, *args, **kwargs):  # type: ignore
        raise NotImplementedError

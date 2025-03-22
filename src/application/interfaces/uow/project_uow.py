from abc import ABC, abstractmethod


class AbstractProjectUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> "AbstractProjectUnitOfWork":
        raise NotImplementedError

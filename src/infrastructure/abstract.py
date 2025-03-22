from abc import ABC, abstractmethod
from typing import TypeVar

from typing_extensions import Generic

D = TypeVar("D")


class InfraStructureEntity(ABC, Generic[D]):
    @abstractmethod
    def to_domain(self) -> D:
        """Преобразует инфраструктурную сущность в доменную"""
        raise NotImplementedError

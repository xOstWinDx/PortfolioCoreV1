from typing import TypeVar

from typing_extensions import Generic

D = TypeVar("D")


class InfraStructureEntity(Generic[D]):
    def to_domain(self) -> D:
        """Преобразует инфраструктурную сущность в доменную"""
        raise NotImplementedError("to_domain not implemented")

from abc import ABC, abstractmethod, ABCMeta
from typing import Callable, Awaitable

from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork


class UseCaseMeta(ABCMeta):
    """Метакласс для автоматического добавления авторизационного декоратора"""

    def __new__(mcs, name, bases, dct):  # type: ignore
        # Объединяем действия с декоратором и абстрактными методами
        if "__call__" in dct:
            dct["__original_call"] = dct["__call__"]
        return super().__new__(mcs, name, bases, dct)

    def __call__(cls, *args, **kwargs):  # type: ignore
        """Вызывается при создании объекта класса и переназначает метод __call__"""
        instance = super().__call__(*args, **kwargs)
        instance.__call__ = instance.__authorize__(instance.__original_call)
        return instance


class AbstractUseCase(ABC, metaclass=UseCaseMeta):
    def __init__(
        self,
        auth: AbstractAuthService,
        uow: AbstractUnitOfWork,
        _authorize: Callable[[Callable[..., Awaitable]], Callable[..., Awaitable]],  # type: ignore
    ):
        self.auth = auth
        self.uow = uow
        self.__authorize__ = _authorize

    @abstractmethod
    async def __call__(self, *args, **kwargs):  # type: ignore
        raise NotImplementedError

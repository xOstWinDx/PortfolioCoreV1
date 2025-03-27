from abc import ABC, abstractmethod

from src.domain.entities.user import User
from src.domain.filters.users import UserFilter


class AbstractUsersRepository(ABC):
    @abstractmethod
    async def register(self, user: User) -> User:
        """Регистрирует пользователя в системе"""
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_filter: UserFilter) -> User | None:
        """Получить пользователя по фильтру (одного)"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_filter: UserFilter) -> bool:
        """Удалить пользователей по фильтру (несколько)"""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, user_filter: UserFilter, update_data: dict[str, object]
    ) -> User:
        """Обновить пользователей по фильтру (несколько)"""
        raise NotImplementedError

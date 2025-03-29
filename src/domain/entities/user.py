from dataclasses import dataclass
from enum import Enum
from functools import total_ordering

from src.domain.entities.base import BaseEntity


@total_ordering
class RolesEnum(Enum):
    GUEST = 0
    BAN = 1
    USER = 2
    MODERATOR = 3
    ADMIN = 4

    def __lt__(self, other):  # type: ignore
        if not isinstance(other, RolesEnum):
            return NotImplemented
        return self.value < other.value

    def __eq__(self, other):  # type: ignore
        if not isinstance(other, RolesEnum):
            return NotImplemented
        return self.value == other.value


@dataclass
class User(BaseEntity):
    email: str
    password: bytes
    username: str
    role: RolesEnum

from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Any

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


@dataclass
class Author:
    id: int
    name: str
    email: str
    photo_url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "photo_url": self.photo_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Author":
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            photo_url=data["photo_url"],
        )

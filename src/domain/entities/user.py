from dataclasses import dataclass

from src.domain.entities.base import BaseEntity


@dataclass
class User(BaseEntity):
    email: str
    password: bytes
    username: str
    roles: list[str]

from dataclasses import dataclass

from src.domain.filters.base import BaseFilter


@dataclass
class UserFilter(BaseFilter):
    email: str | None = None
    username: str | None = None

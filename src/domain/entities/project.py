from dataclasses import dataclass

from src.domain.entities.base import BaseEntity


@dataclass
class Project(BaseEntity):
    title: str
    description: str
    tags: list[str]
    stack: list[str]

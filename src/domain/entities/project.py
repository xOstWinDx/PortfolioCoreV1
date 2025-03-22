from src.domain.entities.base import BaseEntity


class Project(BaseEntity):
    title: str
    description: str
    tags: list[str]
    stack: list[str]

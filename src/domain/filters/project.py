from src.domain.filters.base import BaseFilter


class ProjectFilter(BaseFilter):
    stack: list[str] | None = None

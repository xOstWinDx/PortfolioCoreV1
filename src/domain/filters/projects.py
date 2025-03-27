from datetime import datetime

from src.domain.filters.base import BaseFilter


class ProjectFilter(BaseFilter):
    stack: list[str] | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from src.domain.entities.project import Project
from src.domain.filters.projects import ProjectFilter


class AbstractProjectsRepository(ABC):
    @abstractmethod
    async def get_projects(
        self, filter: ProjectFilter, limit: int, offset: int
    ) -> tuple[Sequence[Project], bool]:
        """Получить все проекты по фильтру и пагинации"""
        raise NotImplementedError

    @abstractmethod
    async def create_project(self, project: Project) -> Project:
        """Создать проект"""
        raise NotImplementedError

    @abstractmethod
    async def update_project(
        self,
        filters: ProjectFilter,
        updated_data: dict[str, str | int | datetime | list[str]],
    ) -> Sequence[Project]:
        """Обновить все проекты подходящие под фильтр"""
        raise NotImplementedError

    @abstractmethod
    async def delete_project(self, filters: ProjectFilter) -> bool:
        """Удалить все проекты по фильтру"""
        raise NotImplementedError

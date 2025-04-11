from datetime import datetime
from typing import Sequence

from asyncpg import UniqueViolationError
from sqlalchemy import Select, Update, Delete
from sqlalchemy.exc import IntegrityError

from src.application.interfaces.repositories.projects import AbstractProjectsRepository
from src.domain.entities.project import Project
from src.domain.exceptions.base import ConflictException
from src.domain.filters.projects import ProjectFilter
from src.infrastructure.models.mapping import to_model
from src.infrastructure.models.project import ProjectModel, TagModel, TechnologyModel
from src.infrastructure.repositories.alchemy_mixin import SQLAlchemyMixin


class SQLProjectsRepository(AbstractProjectsRepository, SQLAlchemyMixin):
    model = ProjectModel

    async def get_projects(
        self, filter: ProjectFilter, limit: int, offset: int
    ) -> tuple[Sequence[Project], bool]:
        query = Select(self.model)
        if filter.date_to:
            query = query.where(self.model.created_at <= filter.date_to)
        if filter.date_from:
            query = query.where(self.model.created_at >= filter.date_from)
        if filter.id:
            query = query.where(self.model.id == filter.id)
        if filter.stack is not None:
            query = query.where(self.model.stack.contains(filter.stack))
        query.offset(offset).limit(limit + 1)
        res = await self.session.execute(query)
        seq: Sequence[ProjectModel] = res.scalars().all()
        has_next = len(seq) > limit
        return [item.to_domain() for item in seq[0:limit]], has_next

    async def _get_or_create_technologies(
        self, technology_names: list[str]
    ) -> list[TechnologyModel]:
        technologies = []
        for name in technology_names:
            # Ищем технологию по имени (если name — это PK)
            technology = await self.session.execute(
                Select(TechnologyModel).where(TechnologyModel.name == name)
            )
            technology = technology.scalar_one_or_none()
            # Если технология не найдена, создаем новую
            if not technology:
                technology = TechnologyModel(name=name)
                self.session.add(technology)
            technologies.append(technology)
        return technologies

    async def _get_or_create_tags(self, tag_names: list[str]) -> list[TagModel]:
        tags = []
        for name in tag_names:
            # Ищем тег по имени (если name — это PK)
            tag = await self.session.execute(
                Select(TagModel).where(TagModel.name == name)
            )
            tag = tag.scalar_one_or_none()
            # Если тег не найден, создаем новый
            if not tag:
                tag = TagModel(name=name)
                self.session.add(tag)
            tags.append(tag)
        return tags

    async def create_project(self, project: Project) -> Project:
        # Получаем или создаем технологии и теги
        technologies = await self._get_or_create_technologies(project.stack)
        tags = await self._get_or_create_tags(project.tags)

        # Преобразуем Project в ProjectModel
        project_model = to_model(project)

        # Устанавливаем связи с технологиями и тегами
        project_model.stack = technologies
        project_model.tags = tags

        # тут может вылететь ошибка, если нарушается согласованность
        try:
            self.session.add(project_model)
            await self.session.flush()
        except (IntegrityError, UniqueViolationError):
            raise ConflictException(f"Project already exists: {project.title}")

        return project_model.to_domain()

    async def update_project(
        self,
        filters: ProjectFilter,
        updated_data: dict[str, str | int | datetime | list[str]],
    ) -> Sequence[Project]:
        self._validate_update_data(updated_data)
        stmt = Update(self.model).values(updated_data).returning(self.model)
        res = await self.session.execute(stmt)
        return [item.to_domain() for item in res.scalars().all()]

    async def delete_project(self, filters: ProjectFilter) -> bool:
        stmt = Delete(self.model).returning(self.model)
        res = await self.session.execute(stmt)
        return bool(res.scalars().all())

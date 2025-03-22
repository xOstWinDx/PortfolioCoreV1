import asyncio
from datetime import datetime
from typing import Sequence

from sqlalchemy import Select, Update, Delete

from src.application.interfaces.repositories.project_repo import (
    AbstractProjectsRepository,
)
from src.domain.entities.project import Project
from src.domain.filters.project import ProjectFilter
from src.infrastructure.models.mapping import to_model
from src.infrastructure.models.project import ProjectModel, TagModel, TechnologyModel
from src.infrastructure.repositories.alchemy_mixin import SQLAlchemyMixin


class ProjectsRepository(AbstractProjectsRepository, SQLAlchemyMixin):
    model = ProjectModel

    async def get_project(
        self, filters: ProjectFilter, limit: int, offset: int
    ) -> Sequence[Project]:
        query = Select(self.model)
        if filters.date_to:
            query = query.where(self.model.created_at <= filters.date_to)
        if filters.date_from:
            query = query.where(self.model.created_at >= filters.date_from)
        if filters.id:
            query = query.where(self.model.id == filters.id)
        if filters.stack is not None:
            query = query.where(self.model.stack.contains(filters.stack))
        query.offset(offset).limit(limit)
        res = await self.session.execute(query)
        seq: Sequence[ProjectModel] = res.scalars().all()
        return [item.to_domain() for item in seq]

    async def _get_or_create_tags(self, tags: list[str]) -> list[TagModel]:
        """Функция проверяет асинхронно все теги и создает их если не находит"""

        async def inner(tag: str) -> TagModel:
            res = await self.session.execute(
                Select(TagModel).where(TagModel.name == tag)
            )
            item: TagModel = res.scalars().one_or_none()
            if item is None:
                item = TagModel(name=tag)
                self.session.add(item)
                await self.session.flush([item])
            return item

        return await asyncio.gather(*[inner(tag) for tag in tags])

    async def _get_or_create_technologies(
        self, technologies: list[str]
    ) -> list[TechnologyModel]:
        """Функция проверяет асинхронно все технологии и создает их если не находит"""

        async def inner(tech: str) -> TechnologyModel:
            res = await self.session.execute(
                Select(TechnologyModel).where(TechnologyModel.name == tech)
            )
            item: TechnologyModel = res.scalars().one_or_none()
            if item is None:
                item = TechnologyModel(name=tech)
                self.session.add(item)
                await self.session.flush([item])
            return item

        return await asyncio.gather(*[inner(tech) for tech in technologies])

    async def create_project(self, project: Project) -> Project:
        project = to_model(
            project,
            tags=await self._get_or_create_tags(project.tags),
            stack=await self._get_or_create_technologies(project.stack),
        )
        self.session.add(project)
        await self.session.flush([project])
        return project.to_domain()

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

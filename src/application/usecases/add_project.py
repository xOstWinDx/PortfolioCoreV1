from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.project import Project
from src.domain.exceptions.base import ConflictException


class AddNewProjectUseCase(AbstractUseCase):
    async def __call__(self, project: Project) -> Project:
        async with self.uow as uow:
            try:
                p = await uow.projects.create_project(project)
            except ConflictException:
                raise ConflictException(f"Project conflict: {project.title}")
            await uow.commit()
            return p

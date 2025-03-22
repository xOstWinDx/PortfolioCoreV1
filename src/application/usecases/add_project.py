from src.application.interfaces.uow.project_uow import AbstractProjectsUnitOfWork
from src.domain.entities.project import Project


class AddNewProjectUseCase:
    def __init__(self, project_uow: AbstractProjectsUnitOfWork):
        self.project_uow = project_uow

    async def __call__(self, project: Project) -> bool:
        async with self.project_uow as uow:
            await uow.projects.create_project(project)
            await uow.commit()
        return True

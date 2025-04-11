from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.projects import ProjectsService
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.project import Project


class GetProjectsUseCase(AbstractUseCase):
    def __init__(
        self,
        auth: AbstractAuthService,
        uow: AbstractUnitOfWork,
        projects: ProjectsService,
    ):
        super().__init__(auth=auth, uow=uow)
        self.projects = projects

    async def __call__(
        self, offset: int = 0, limit: int = 10
    ) -> tuple[list[Project], bool]:
        projects = await self.projects.get_projects(limit=limit, offset=offset)
        return projects

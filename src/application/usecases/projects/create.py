from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.projects import ProjectsService
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.project import Project
from src.domain.entities.user import Author
from src.domain.exceptions.auth import SubjectNotFoundError
from src.domain.filters.users import UserFilter
from src.domain.value_objects.auth import AuthorizationContext


class CreateProjectUseCase(AbstractUseCase):
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        auth: AbstractAuthService,
        projects: ProjectsService,
    ):
        super().__init__(auth=auth, uow=uow)
        self.projects = projects

    async def __call__(
        self, project: Project, context: AuthorizationContext
    ) -> Project:
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(id=context.user_id))
            if user is None:
                raise SubjectNotFoundError("User not found")
            project.author = Author(
                id=user.id,  # type: ignore
                name=user.username,
                email=user.email,
                photo_url="Coming soon...",
            )
            return await self.projects.create_project(project)

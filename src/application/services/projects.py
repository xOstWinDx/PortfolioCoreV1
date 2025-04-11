from src.application.interfaces.clients.cache import AbstractCacheClient
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.config import CONFIG
from src.domain.entities.project import Project
from src.domain.filters.projects import ProjectFilter


class ProjectsService:
    def __init__(self, uow: AbstractUnitOfWork, cache_client: AbstractCacheClient):
        self.uow = uow
        self.cache_client = cache_client

    @staticmethod
    def make_project_key(
        project_id: str | int = "*", offset: str | int = "*", limit: str | int = "*"
    ) -> str:
        return f"project:{project_id}:{offset}:{limit}"

    async def create_project(self, project: Project) -> Project:
        project = await self.uow.projects.create_project(project)
        if project:
            keys = await self.cache_client.keys(self.make_project_key())
            await self.cache_client.delete(*keys)
        return project

    async def get_projects(self, limit: int, offset: int) -> tuple[list[Project], bool]:
        if cache := await self.cache_client.get(
            self.make_project_key(limit=limit, offset=offset)
        ):
            return [Project.from_dict(project) for project in cache["data"]], cache[  # type: ignore
                "has_next"
            ]
        projects, has_next = await self.uow.projects.get_projects(
            filter=ProjectFilter(), limit=limit, offset=offset
        )
        await self.cache_client.set(
            key=self.make_project_key(limit=limit, offset=offset),
            data={
                "data": [project.to_dict() for project in projects],
                "has_next": has_next,
            },
            expiration=CONFIG.PROJECTS_CACHE_EXPIRE_SECONDS,
        )
        return list(projects), has_next

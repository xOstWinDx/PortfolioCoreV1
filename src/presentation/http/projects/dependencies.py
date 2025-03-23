from collections.abc import AsyncGenerator

from src.application.usecases.add_project import AddNewProjectUseCase
from src.container import Container

container = Container()


async def get_create_project_use_case() -> AsyncGenerator[AddNewProjectUseCase, None]:
    yield container.create_project_use_case()

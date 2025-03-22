from fastapi import APIRouter, Depends

from src.application.usecases.add_project import AddNewProjectUseCase
from src.container import Container
from src.infrastructure.schemas.project import ProjectResponse, ProjectSchema

router = APIRouter(prefix="/projects", tags=["projects"])

container = Container()


@router.post("/")
async def create_project(
    project: ProjectSchema,
    use_case: AddNewProjectUseCase = Depends(container.create_project_use_case),
) -> ProjectResponse:
    res = await use_case(project.to_domain())
    return ProjectResponse.model_validate(res, from_attributes=True)

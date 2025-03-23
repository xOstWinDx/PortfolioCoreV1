from fastapi import APIRouter, Depends

from src.application.usecases.add_project import AddNewProjectUseCase
from src.infrastructure.schemas.project import ProjectResponse, ProjectSchema
from src.presentation.http.projects.dependencies import get_create_project_use_case

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/")
async def create_project(
    project: ProjectSchema,
    use_case: AddNewProjectUseCase = Depends(get_create_project_use_case),
) -> ProjectResponse:
    res = await use_case(project.to_domain())
    return ProjectResponse.model_validate(res, from_attributes=True)

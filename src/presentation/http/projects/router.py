from typing import Annotated

from dependency_injector.wiring import inject
from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from src.application.usecases.add_project import AddNewProjectUseCase
from src.domain.exceptions.base import ConflictException
from src.infrastructure.schemas.project import ProjectResponse, ProjectSchema
from src.presentation.http.dependencies import access_token_schema
from src.presentation.http.projects.dependencies import container

router = APIRouter(prefix="/projects", tags=["projects"])

container.wire(modules=[__name__])


@router.post("/", status_code=201)
@inject
async def create_project(
    project: ProjectSchema,
    use_case: Annotated[AddNewProjectUseCase, container.create_project_use_case],
    access_token: Annotated[str, Depends(access_token_schema)],
) -> ProjectResponse:
    try:
        res = await use_case(
            project.to_domain(),
            credentials=container.credentials(
                access_token=access_token, refresh_token=""
            ),
        )
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return ProjectResponse.model_validate(res, from_attributes=True)

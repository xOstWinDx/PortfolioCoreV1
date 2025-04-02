from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, Depends

from starlette import status
from starlette.requests import Request

from src.application.authorize import UseCaseGuard
from src.application.interfaces.credentials import Credentials  # noqa: F401
from src.application.usecases.add_project import CreateProjectUseCase
from src.container import container
from src.context import CredentialsHolder
from src.domain.exceptions.base import ConflictException
from src.domain.value_objects.auth import AuthorizationContext  # noqa: F401
from src.infrastructure.schemas.project import ProjectResponse, ProjectSchema
from src.presentation.http.dependencies import credentials_schema, get_creds_holder

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", status_code=201)
@inject
async def create_project(
    project: ProjectSchema,
    request: Request,
    creds_holder: Annotated[CredentialsHolder, Depends(get_creds_holder)],
    credentials: Annotated[credentials_schema, Depends()],  # type: ignore
    guard: UseCaseGuard[CreateProjectUseCase] = Depends(
        Provide["create_project_use_case"]
    ),
) -> ProjectResponse:
    try:
        guard.configure(
            credentials=credentials,
            creds_holder=creds_holder,
            device_id=str(request.client.host),
        )
        async with guard as (use_case, _, _):  # type: CreateProjectUseCase # type: ignore[no-redef]
            res = await use_case(
                project=project.to_domain(),
                credentials=credentials,
            )
            return ProjectResponse.model_validate(res, from_attributes=True)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


container.wire(modules=[__name__])  # должен быть внизу

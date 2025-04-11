from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, HTTPException, Depends, Query
from starlette import status
from starlette.requests import Request

from src.application.authorize import UseCaseGuard
from src.application.interfaces.credentials import Credentials  # noqa: F401
from src.application.usecases.projects.create import CreateProjectUseCase
from src.application.usecases.projects.get import GetProjectsUseCase
from src.container import container
from src.context import CredentialsHolder
from src.domain.exceptions.base import ConflictException
from src.domain.value_objects.auth import AuthorizationContext  # noqa: F401
from src.infrastructure.schemas.project import (
    ReadProjectSchema,
    CreateProjectSchema,
    ProjectsResponse,
)
from src.presentation.http.dependencies import credentials_schema, get_creds_holder

router = APIRouter(prefix="/projects", tags=["projects"])


# ────────────────
# TODO [03.04.2025 | High]
# Assigned to: stark
# Description: Добавить ендпоинт для получения проектов
# Steps:
#   - Сделать ProjectService соединить там репозиторий и кеш
#   - реализовать пагинацию
#   -
# ────────────────


@router.post("/", status_code=201)
@inject
async def create_project(
    project: CreateProjectSchema,
    request: Request,
    creds_holder: Annotated[CredentialsHolder, Depends(get_creds_holder)],
    credentials: Annotated[credentials_schema, Depends()],  # type: ignore
    guard: UseCaseGuard[CreateProjectUseCase] = Depends(
        Provide["create_project_use_case"]
    ),
) -> ReadProjectSchema:
    try:
        guard.configure(
            credentials=credentials,
            creds_holder=creds_holder,
            device_id=str(request.client.host),
        )
        async with guard as (use_case, context, _):  # type: CreateProjectUseCase, AuthorizationContext, Credentials
            res = await use_case(
                project=project.to_domain(),
                context=context,
            )
            return ReadProjectSchema.model_validate(res, from_attributes=True)
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/", status_code=200)
@inject
async def get_projects(
    request: Request,
    offset: int,
    creds_holder: Annotated[CredentialsHolder, Depends(get_creds_holder)],
    credentials: Annotated[credentials_schema, Depends()],  # type: ignore
    limit: int = Query(default=20, le=40, gt=0),
    guard: UseCaseGuard[GetProjectsUseCase] = Depends(Provide["get_projects_use_case"]),
) -> ProjectsResponse:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, _):  # type: GetProjectsUseCase, AuthorizationContext, Credentials
        projects = await use_case(offset=offset, limit=limit)
        return ProjectsResponse.model_validate(
            {"projects": projects[0], "has_next": projects[1]}, from_attributes=True
        )


container.wire(modules=[__name__])  # должен быть внизу

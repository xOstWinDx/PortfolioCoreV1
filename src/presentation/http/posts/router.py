from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.params import Query
from starlette.requests import Request

from src.application.authorize import UseCaseGuard
from src.application.interfaces.credentials import Credentials
from src.application.usecases.posts.create_post import CreatePostUseCase
from src.application.usecases.posts.get_posts import GetPostsUseCase
from src.container import Container
from src.context import CredentialsHolder
from src.domain.value_objects.auth import AuthorizationContext  # noqa: F401
from src.infrastructure.schemas.post import (
    CreatePostSchema,
    ReadPostSchema,
    PostsResponseSchema,
)
from src.presentation.http.dependencies import credentials_schema, get_creds_holder

container = Container()
router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=201)
@inject
async def create_post(
    post: CreatePostSchema,
    request: Request,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[CreatePostUseCase] = Depends(Provide["create_post_use_case"]),
) -> ReadPostSchema:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (CreatePostUseCase, AuthorizationContext, Credentials)
        res = await use_case(post=post.to_domain(), context=context)
        return ReadPostSchema.model_validate(res, from_attributes=True)


@router.get("/", status_code=200)
@inject
async def get_posts(
    request: Request,
    last_id: str | None = None,
    limit: int = Query(default=20, le=40, gt=0),
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[GetPostsUseCase] = Depends(Provide["get_posts_use_case"]),
) -> PostsResponseSchema:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (GetPostsUseCase, AuthorizationContext, Credentials)
        posts = await use_case(last_id=last_id, limit=limit)
        if not posts:
            return PostsResponseSchema.model_validate(
                {"posts": [], "has_next": False}, from_attributes=True
            )
        return PostsResponseSchema.model_validate(
            {"posts": posts[0], "has_next": posts[1]}, from_attributes=True
        )


# ────────────────
# TODO [06.04.2025 | High]
# Assigned to: stark
# Description: Реализовать оценку постов
# Steps:
#   - Можно лайкать
#   - Можно дизлайкать
# ────────────────


# ────────────────
# TODO [06.04.2025 | High]
# Assigned to: stark
# Description: Реализовать взаимодейсвтие с комментариями
# Steps:
#   - Комментарии можно создавать
#   - На комментарии можно отвечать
#   - Комментарии можно лайкать и дизлайкать
# ────────────────
container.wire(modules=[__name__])

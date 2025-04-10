from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from starlette import status
from starlette.requests import Request

from src.application.authorize import UseCaseGuard
from src.application.interfaces.credentials import Credentials
from src.application.usecases.posts.comments.answers.create import CreateAnswerUseCase
from src.application.usecases.posts.comments.answers.get import GetAnswersUseCase
from src.application.usecases.posts.comments.create import CreateCommentUseCase
from src.application.usecases.posts.comments.get import GetCommentsUseCase
from src.application.usecases.posts.comments.rate import RateCommentUseCase
from src.application.usecases.posts.create import CreatePostUseCase
from src.application.usecases.posts.get import GetPostsUseCase
from src.application.usecases.posts.rate import RatePostUseCase
from src.container import Container
from src.context import CredentialsHolder
from src.domain.exceptions.auth import SubjectNotFoundError
from src.domain.value_objects.auth import AuthorizationContext  # noqa: F401
from src.infrastructure.schemas.post import (
    CreatePostSchema,
    ReadPostSchema,
    PostsResponseSchema,
    CreateCommentSchema,
    ReadCommentSchema,
    CommentsResponseSchema,
    CreateAnswerSchema,
    ReadAnswerSchema,
    AnswersResponseSchema,
)
from src.presentation.http.dependencies import credentials_schema, get_creds_holder

container = Container()
router = APIRouter(prefix="/posts", tags=["posts"])

# region Posts


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
        if not posts or not posts[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
            )
        return PostsResponseSchema.model_validate(
            {"posts": posts[0], "has_next": posts[1]}, from_attributes=True
        )


@router.post("/{post_id}/like", status_code=201)
@inject
async def like_post(
    request: Request,
    post_id: str,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RatePostUseCase] = Depends(Provide["rate_post_use_case"]),
) -> dict[str, str | int]:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (RatePostUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(mode="like", post_id=post_id, context=context)
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if res:
            return {"message": "Post has been liked", "post_id": post_id, "status": 201}
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Post has been already liked"
        )


@router.post("/{post_id}/dislike", status_code=201)
@inject
async def dislike_post(
    request: Request,
    post_id: str,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RatePostUseCase] = Depends(Provide["rate_post_use_case"]),
) -> dict[str, str | int]:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (RatePostUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(mode="dislike", post_id=post_id, context=context)
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if res:
            return {
                "message": "Post has been disliked",
                "post_id": post_id,
                "status": 201,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Post has been already disliked",
        )


# endregion


# region Comments
@router.post("/{post_id}/comments", status_code=201)
@inject
async def create_comment(
    request: Request,
    post_id: str,
    comment: CreateCommentSchema,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[CreateCommentUseCase] = Depends(
        Provide["create_comment_use_case"]
    ),
) -> ReadCommentSchema:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (CreateCommentUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(
                post_id=post_id, comment=comment.to_domain(post_id), context=context
            )
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        return ReadCommentSchema.model_validate(res, from_attributes=True)


@router.get("/{post_id}/comments", status_code=200)
@inject
async def get_comments(
    request: Request,
    post_id: str,
    last_id: str | None = None,
    limit: int = Query(default=20, le=40, gt=0),
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[GetCommentsUseCase] = Depends(Provide["get_comments_use_case"]),
) -> CommentsResponseSchema:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (GetCommentsUseCase, AuthorizationContext, Credentials)
        comments = await use_case(
            post_id=post_id,
            last_id=last_id,
            limit=limit,
        )
        if not comments or not comments[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found"
            )
        return CommentsResponseSchema.model_validate(
            {"comments": comments[0], "has_next": comments[1]}, from_attributes=True
        )


@router.post("/{post_id}/comments/{comment_id}/like", status_code=201)
@inject
async def like_comment(
    request: Request,
    post_id: str,
    comment_id: str,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RateCommentUseCase] = Depends(Provide["rate_comment_use_case"]),
) -> dict[str, str | int]:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (RateCommentUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(
                mode="like", post_id=post_id, context=context, comment_id=comment_id
            )
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if res:
            return {
                "message": "Comment has been liked",
                "comment_id": comment_id,
                "status": 201,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Comment has been already liked",
        )


@router.post("/{post_id}/comments/{comment_id}/dislike", status_code=201)
@inject
async def dislike_comment(
    request: Request,
    post_id: str,
    comment_id: str,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RateCommentUseCase] = Depends(Provide["rate_comment_use_case"]),
) -> dict[str, str | int]:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (RateCommentUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(
                mode="dislike", post_id=post_id, context=context, comment_id=comment_id
            )
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if res:
            return {
                "message": "Comment has been disliked",
                "comment_id": comment_id,
                "status": 201,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Comment has been already disliked",
        )


# endregion

# region Answers


@router.post("/{post_id}/comments/{comment_id}/replies", status_code=201)
@inject
async def create_answer(
    post_id: str,
    comment_id: str,
    answer: CreateAnswerSchema,
    request: Request,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[CreateAnswerUseCase] = Depends(
        Provide["create_answer_use_case"]
    ),
) -> ReadAnswerSchema:
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (CreateAnswerUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(
                post_id=post_id,
                comment_id=comment_id,
                answer=answer.to_domain(post_id=post_id),
                context=context,
            )
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        return ReadAnswerSchema.model_validate(res, from_attributes=True)


@router.get("/{post_id}/comments/{comment_id}/replies", status_code=200)
@inject
async def get_answers(
    request: Request,
    comment_id: str,
    post_id: str,
    last_id: str | None = None,
    limit: int = Query(default=20, le=40, gt=0),
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[GetAnswersUseCase] = Depends(Provide["get_answers_use_case"]),
) -> AnswersResponseSchema:
    _ = post_id  # он тут не нужен, но должен быть по REST
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (GetAnswersUseCase, AuthorizationContext, Credentials)
        answers = await use_case(
            comment_id=comment_id,
            last_id=last_id,
            limit=limit,
        )
        if not answers or not answers[0]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Answers not found"
            )
        return AnswersResponseSchema.model_validate(
            {"answers": answers[0], "has_next": answers[1]}, from_attributes=True
        )


@router.post(
    "/{post_id}/comments/{comment_id}/replies/{answer_id}/like", status_code=201
)
@inject
async def like_answer(
    request: Request,
    post_id: str,
    comment_id: str,
    answer_id: str,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RateCommentUseCase] = Depends(Provide["rate_comment_use_case"]),
) -> dict[str, str | int]:
    _ = comment_id  # он тут не нужен, но должен быть по REST
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (RateCommentUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(
                mode="like", post_id=post_id, context=context, comment_id=answer_id
            )
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if res:
            return {
                "message": "Answer has been liked",
                "answer_id": answer_id,
                "status": 201,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Answer has been already liked"
        )


@router.post(
    "/{post_id}/comments/{comment_id}/replies/{answer_id}/dislike", status_code=201
)
@inject
async def dislike_answer(
    request: Request,
    post_id: str,
    comment_id: str,
    answer_id: str,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RateCommentUseCase] = Depends(Provide["rate_comment_use_case"]),
) -> dict[str, str | int]:
    _ = comment_id  # он тут не нужен, но должен быть по REST
    guard.configure(
        credentials=credentials,
        creds_holder=creds_holder,
        device_id=request.client.host,
    )
    async with guard as (use_case, context, creds):  # type: (RateCommentUseCase, AuthorizationContext, Credentials)
        try:
            res = await use_case(
                mode="dislike", post_id=post_id, context=context, comment_id=answer_id
            )
        except SubjectNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if res:
            return {
                "message": "Answer has been disliked",
                "answer_id": answer_id,
                "status": 201,
            }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer has been already disliked",
        )


# endregion

container.wire(modules=[__name__])

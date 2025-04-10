from typing import Literal

from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.posts import PostsService
from src.application.usecases.abs import AbstractUseCase
from src.domain.exceptions.auth import AccessDeniedError, SubjectNotFoundError
from src.domain.filters.users import UserFilter
from src.domain.value_objects.auth import AuthorizationContext


class RatePostUseCase(AbstractUseCase):
    def __init__(
        self, auth: AbstractAuthService, uow: AbstractUnitOfWork, posts: PostsService
    ):
        super().__init__(auth=auth, uow=uow)
        self.posts = posts

    async def __call__(
        self,
        mode: Literal["like", "dislike"],
        post_id: str,
        context: AuthorizationContext,
    ) -> bool:
        if context.user_id is None:
            raise AccessDeniedError("You must be logged in to rate a post")

        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(id=context.user_id))
        if user is None:
            raise SubjectNotFoundError("User not found")

        async with self.posts:
            if mode == "like":
                return await self.posts.like_post(
                    post_id=post_id, user_id=context.user_id
                )
            elif mode == "dislike":
                return await self.posts.dislike_post(
                    post_id=post_id, user_id=context.user_id
                )
            else:
                raise ValueError(f"Invalid mode: {mode}")

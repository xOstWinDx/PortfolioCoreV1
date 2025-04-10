from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.posts import PostsService
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.post import Comment, Author
from src.domain.exceptions.auth import AccessDeniedError
from src.domain.filters.users import UserFilter
from src.domain.value_objects.auth import AuthorizationContext


class CreateAnswerUseCase(AbstractUseCase):
    def __init__(
        self, auth: AbstractAuthService, uow: AbstractUnitOfWork, posts: PostsService
    ):
        super().__init__(auth=auth, uow=uow)
        self.posts = posts

    async def __call__(
        self,
        post_id: str,
        comment_id: str,
        answer: Comment,
        context: AuthorizationContext,
    ) -> Comment:
        if not context.user_id:
            raise AccessDeniedError("You must be logged in to create a comment")
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(id=context.user_id))
        if user is None:
            raise AccessDeniedError("You must be logged in to create a comment")
        author = Author(
            id=user.id,  # type: ignore
            name=user.username,
            email=user.email,
            photo_url="Coming soon...",
        )
        answer.author = author
        async with self.posts:
            return await self.posts.create_answer(
                post_id=post_id, answer=answer, comment_id=comment_id
            )

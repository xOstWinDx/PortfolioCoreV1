from src.application.interfaces.services.auth import AbstractAuthService
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.services.posts import PostsService
from src.application.usecases.abs import AbstractUseCase
from src.domain.entities.post import Post, Author
from src.domain.exceptions.auth import AccessDeniedError
from src.domain.filters.users import UserFilter
from src.domain.value_objects.auth import AuthorizationContext


class CreatePostUseCase(AbstractUseCase):
    def __init__(
        self, auth: AbstractAuthService, uow: AbstractUnitOfWork, posts: PostsService
    ):
        super().__init__(auth=auth, uow=uow)
        self.posts = posts

    async def __call__(self, post: Post, context: AuthorizationContext) -> Post:
        async with self.uow as uow:
            user = await uow.users.get_user(UserFilter(id=context.user_id))
        if user is None:
            raise AccessDeniedError("You must be logged in to create a post")
        async with self.posts:
            post.author = Author(
                id=user.id,  # type: ignore
                name=user.username,
                email=user.email,
                photo_url="Coming soon...",
            )
            return await self.posts.create_post(post=post)

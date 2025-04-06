from src.application.interfaces.clients.cache import AbstractCacheClient
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.config import CONFIG
from src.domain.entities.post import Post, Comment


class PostsService:
    def __init__(self, uow: AbstractUnitOfWork, cache_client: AbstractCacheClient):
        self.uow = uow
        self.cache_client = cache_client

    @staticmethod
    def comments_key(
        *, post_id: str = "*", last_id: str | None = "*", limit: int | str = "*"
    ) -> str:
        return f"comments:{post_id}:{last_id}:{limit}"

    @staticmethod
    def answers_key(
        *, parent_id: str = "*", last_id: str | None = "*", limit: int | str = "*"
    ) -> str:
        return f"answers:{parent_id}:{last_id}:{limit}"

    async def __aenter__(self) -> None:
        await self.uow.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        await self.uow.__aexit__(exc_type, exc, tb)

    async def get_posts(
        self, last_id: str | None = None, limit: int = 20
    ) -> list[Post] | None:
        if cached := await self.cache_client.get(f"posts:{last_id}:{limit}"):
            return cached

        posts = await self.uow.posts.get_posts(last_id=last_id, limit=limit)

        await self.cache_client.set(
            key=f"posts:{last_id}:{limit}",
            data=posts,
            expiration=CONFIG.POSTS_CACHE_EXPIRE_SECONDS,
        )

        return posts

    async def create_post(self, post: Post) -> Post:
        return await self.uow.posts.create_post(post=post)

    async def like_post(self, post_id: str, user_id: int) -> bool:
        return await self.uow.posts.like_post(post_id=post_id, user_id=user_id)

    async def dislike_post(self, post_id: str, user_id: int) -> bool:
        return await self.uow.posts.dislike_post(post_id=post_id, user_id=user_id)

    async def get_comments(
        self, post_id: str, last_id: str | None = None, limit: int = 10
    ) -> list[Comment] | None:
        key = self.comments_key(post_id=post_id, last_id=last_id, limit=limit)
        if cached := await self.cache_client.get(key):
            return cached

        comments = await self.uow.posts.get_comments(
            post_id=post_id, last_id=last_id, limit=limit
        )

        await self.cache_client.set(
            key=key, data=comments, expiration=CONFIG.COMMENTS_CACHE_EXPIRE_SECONDS
        )

        return comments

    async def create_comment(self, post_id: str, comment: Comment) -> Comment:
        if res := await self.uow.posts.create_comment(comment):
            key = self.comments_key(post_id=post_id)
            keys = await self.cache_client.keys(key)
            await self.cache_client.delete(*keys)
        return res

    async def like_comment(self, post_id: str, comment_id: str, user_id: int) -> bool:
        if res := await self.uow.posts.like_comment(
            comment_id=comment_id, user_id=user_id
        ):
            key = self.comments_key(post_id=post_id)
            keys = await self.cache_client.keys(key)
            await self.cache_client.delete(*keys)
        return res

    async def dislike_comment(
        self, post_id: str, comment_id: str, user_id: int
    ) -> bool:
        if res := await self.uow.posts.dislike_comment(
            comment_id=comment_id, user_id=user_id
        ):
            key = self.comments_key(post_id=post_id)
            keys = await self.cache_client.keys(key)
            await self.cache_client.delete(*keys)
        return res

    async def create_answer(
        self, answer: Comment, comment_id: str, post_id: str
    ) -> Comment:
        if res := await self.uow.posts.create_answer(
            answer=answer, comment_id=comment_id
        ):
            key = self.comments_key(post_id=post_id)
            keys = await self.cache_client.keys(key)
            await self.cache_client.delete(*keys)
        return res

    async def get_answers(
        self, comment_id: str, last_id: str | None = None, limit: int = 10
    ) -> list[Comment] | None:
        key = self.answers_key(parent_id=comment_id, last_id=last_id, limit=limit)
        if cached := await self.cache_client.get(key):
            return cached

        answers = await self.uow.posts.get_answers(
            comment_id=comment_id, last_id=last_id, limit=limit
        )

        await self.cache_client.set(
            key=key, data=answers, expiration=CONFIG.COMMENTS_CACHE_EXPIRE_SECONDS
        )

        return answers

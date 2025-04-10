import logging
from typing import Literal

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from src.application.interfaces.repositories.posts import AbstractPostsRepository
from src.config import CONFIG
from src.domain.entities.post import Post, Comment
from src.domain.exceptions.auth import SubjectNotFoundError


class MongoPostsRepository(AbstractPostsRepository):
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.mongo_client = mongo_client
        self.db = self.mongo_client[CONFIG.BLOG_DB_NAME]

    async def get_posts(
        self,
        last_id: str | None = None,
        limit: int = 20,
        sort: Literal["asc", "desc"] = "desc",
    ) -> tuple[list[Post], bool]:
        pipline = [
            {
                "$match": {
                    **(
                        {
                            "_id": {"$lt": ObjectId(last_id)}
                            if sort == "desc"
                            else {"$gt": ObjectId(last_id)}
                        }
                        if last_id
                        else {}
                    )
                }
            },
            {"$sort": {"_id": -1 if sort == "desc" else 1}},
            {"$limit": limit + 1},
            {
                "$lookup": {
                    "from": "comments",
                    "localField": "_id",
                    "foreignField": "post_id",
                    "as": "recent_comments",
                    "pipeline": [
                        {"$match": {"parent_id": None}},  # только корневые комментарии
                        {"$sort": {"_id": -1}},
                        {"$limit": 5},
                    ],
                }
            },
        ]
        cursor = self.db["posts"].aggregate(pipline)
        result = [Post.from_dict(post) async for post in cursor]
        has_next = len(result) > limit
        return result[:limit], has_next

    async def create_post(self, post: Post) -> Post:
        res = await self.db["posts"].insert_one(
            {
                "title": post.title,
                "content": post.content,
                "author": post.author.to_dict(),  # type: ignore
                "dislikes": [],
                "likes": [],
                "created_at": post.created_at.isoformat(),
                "comments_count": 0,
            }
        )
        post.id = str(res.inserted_id)
        return post

    async def like_post(self, post_id: str, user_id: int) -> bool:
        if not await self.db["posts"].find_one({"_id": ObjectId(post_id)}):
            logging.error(f"Post with id {post_id} not found")
            raise SubjectNotFoundError("Post not found")

        res = await self.db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"likes": user_id},
                "$pull": {"dislikes": user_id},
            },
        )
        return bool(res.modified_count)

    async def get_comments(
        self,
        post_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> tuple[list[Comment], bool]:
        pipline = [
            {
                "$match": {
                    "post_id": ObjectId(post_id),
                    "parent_id": None,  # только корневые комментарии
                    **(
                        {
                            "_id": {"$lt": ObjectId(last_id)}
                            if sort == "desc"
                            else {"$gt": ObjectId(last_id)}
                        }
                        if last_id
                        else {}
                    ),
                }
            },
            {"$sort": {"_id": -1 if sort == "desc" else 1}},
            {"$limit": limit + 1},
        ]
        comments = [
            Comment.from_dict(comment)
            async for comment in self.db["comments"].aggregate(pipline)
        ]
        has_next = len(comments) > limit
        return comments[:limit], has_next

    async def dislike_post(self, post_id: str, user_id: int) -> bool:
        if not await self.db["posts"].find_one({"_id": ObjectId(post_id)}):
            logging.error(f"Post with id {post_id} not found")
            raise SubjectNotFoundError("Post not found")

        res = await self.db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"dislikes": user_id},
                "$pull": {"likes": user_id},
            },
        )
        return bool(res.modified_count)

    async def create_comment(self, comment: Comment) -> Comment:
        if not await self.db["posts"].find_one({"_id": ObjectId(comment.post_id)}):
            logging.error(f"Post with id {comment.post_id} not found")
            raise SubjectNotFoundError("Post not found")

        res = await self.db["comments"].insert_one(
            {
                "text": comment.text,
                "author": comment.author.to_dict(),  # type: ignore
                "parent_id": None,
                "post_id": ObjectId(comment.post_id),
                "dislikes": [],
                "likes": [],
                "answers_count": 0,
                "created_at": comment.created_at.isoformat(),
            }
        )
        comments_count = await self.db["comments"].count_documents(
            {"post_id": ObjectId(comment.post_id)}
        )
        await self.db["posts"].update_one(
            {"_id": ObjectId(comment.post_id)},
            {"$set": {"comments_count": comments_count}},
        )

        comment.id = str(res.inserted_id)
        return comment

    async def get_answers(
        self,
        comment_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> tuple[list[Comment], bool]:
        pipeline = [
            {
                "$match": {
                    "parent_id": ObjectId(comment_id),
                    **(
                        {
                            "_id": {"$lt": ObjectId(last_id)}
                            if sort == "desc"
                            else {"$gt": ObjectId(last_id)}
                        }
                        if last_id
                        else {}
                    ),
                },
            },
            {"$sort": {"_id": -1 if sort == "desc" else 1}},
            {"$limit": limit + 1},
        ]
        comments = [
            Comment.from_dict(comment)
            async for comment in self.db["comments"].aggregate(pipeline)
        ]
        has_next = len(comments) > limit
        return comments[:limit], has_next

    async def create_answer(self, answer: Comment, comment_id: str) -> Comment:
        if not await self.db["comments"].find_one({"_id": ObjectId(comment_id)}):
            logging.error(f"Comment with id {comment_id} not found")
            raise SubjectNotFoundError("Comment not found")

        if not await self.db["posts"].find_one({"_id": ObjectId(answer.post_id)}):
            logging.error(f"Post with id {answer.post_id} not found")
            raise SubjectNotFoundError("Post not found")

        res = await self.db["comments"].insert_one(
            {
                "text": answer.text,
                "author": answer.author.to_dict(),  # type: ignore
                "parent_id": ObjectId(comment_id),
                "post_id": ObjectId(answer.post_id),
                "dislikes": [],
                "likes": [],
                "answers_count": 0,
                "created_at": answer.created_at.isoformat(),
            }
        )
        answers_count = await self.db["comments"].count_documents(
            {"parent_id": ObjectId(comment_id)}
        )
        await self.db["comments"].update_one(
            {"_id": ObjectId(comment_id)}, {"$set": {"answers_count": answers_count}}
        )
        answer.id = str(res.inserted_id)
        return answer

    async def like_comment(self, comment_id: str, user_id: int) -> bool:
        if not await self.db["comments"].find_one({"_id": ObjectId(comment_id)}):
            logging.error(f"Comment with id {comment_id} not found")
            raise SubjectNotFoundError("Comment not found")

        res = await self.db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$addToSet": {"likes": user_id},
                "$pull": {"dislikes": user_id},
            },
        )
        return bool(res.modified_count)

    async def dislike_comment(self, comment_id: str, user_id: int) -> bool:
        if not await self.db["comments"].find_one({"_id": ObjectId(comment_id)}):
            logging.error(f"Comment with id {comment_id} not found")
            raise SubjectNotFoundError("Comment not found")

        res = await self.db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$addToSet": {"dislikes": user_id},
                "$pull": {"likes": user_id},
            },
        )
        return bool(res.modified_count)

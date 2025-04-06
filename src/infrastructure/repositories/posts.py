from datetime import datetime
from typing import Literal

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from src.application.interfaces.repositories.posts import AbstractPostsRepository
from src.config import CONFIG
from src.domain.entities.post import Post, Comment


class MongoPostsRepository(AbstractPostsRepository):
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.mongo_client = mongo_client
        self.db = self.mongo_client[CONFIG.BLOG_DB_NAME]

    async def get_posts(
        self,
        last_id: str | None = None,
        limit: int = 20,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Post]:
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
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "comments",
                    "localField": "_id",
                    "foreignField": "post_id",
                    "as": "comments",
                    "pipeline": [{"$sort": {"_id": -1}}, {"$limit": 5}],
                }
            },
        ]
        cursor = self.db["posts"].aggregate(pipline)
        result = [
            Post(
                id=str(post.get("_id")),
                title=post.get("title"),
                content=post.get("content"),
                author_id=post.get("author_id"),
                author_name=post.get("author_name"),
                author_email=post.get("author_email"),
                author_photo_url=post.get("author_photo_url"),
                dislikes=post.get("dislikes"),
                likes=post.get("likes"),
                created_at=datetime.fromisoformat(post["created_at"]),
                comments_count=post.get("comments_count", 0),
                recent_comments=post.get("comments", []),
            )
            async for post in cursor
        ]
        return result

    async def create_post(self, post: Post) -> Post:
        res = await self.db["posts"].insert_one(
            {
                "title": post.title,
                "content": post.content,
                "author_id": post.author_id,
                "author_name": post.author_name,
                "author_email": post.author_email,
                "author_photo_url": post.author_photo_url,
                "dislikes": [],
                "likes": [],
                "created_at": post.created_at.isoformat(),
                "comments_count": 0,
            }
        )
        post.id = str(res.inserted_id)
        return post

    async def like_post(self, post_id: str, user_id: int) -> bool:
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
    ) -> list[Comment]:
        pipline = [
            {
                "$match": {
                    "post_id": ObjectId(post_id),
                    **(
                        {
                            "_id": {"$lt": last_id}
                            if sort == "desc"
                            else {"$gt": last_id}
                        }
                        if last_id
                        else {}
                    ),
                }
            },
            {"$sort": {"_id": -1 if sort == "desc" else 1}},
            {"$limit": limit},
        ]
        return [
            Comment(
                id=str(comment.get("_id")),
                text=comment.get("text"),
                author_id=comment.get("author_id"),
                author_name=comment.get("author_name"),
                author_email=comment.get("author_email"),
                author_photo_url=comment.get("author_photo_url"),
                parent_id=comment.get("parent_id"),
                post_id=comment.get("post_id"),
                dislikes=comment.get("dislikes"),
                likes=comment.get("likes"),
                answers_count=comment.get("answers_count"),
                created_at=datetime.fromisoformat(comment["created_at"]),
            )
            async for comment in self.db["comments"].aggregate(pipline)
        ]

    async def dislike_post(self, post_id: str, user_id: int) -> bool:
        res = await self.db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"dislikes": user_id},
                "$pull": {"likes": user_id},
            },
        )
        return bool(res.modified_count)

    async def create_comment(self, comment: Comment) -> Comment:
        res = await self.db["comments"].insert_one(
            {
                "text": comment.text,
                "author_id": comment.author_id,
                "author_name": comment.author_name,
                "author_email": comment.author_email,
                "author_photo_url": comment.author_photo_url,
                "parent_id": None,
                "post_id": comment.post_id,
                "dislikes": [],
                "likes": [],
                "answers_count": 0,
                "created_at": comment.created_at.isoformat(),
            }
        )
        await self.db["posts"].update_one(
            {"_id": ObjectId(comment.post_id)}, {"$inc": {"comments_count": 1}}
        )

        comment.id = str(res.inserted_id)
        return comment

    async def get_answers(
        self,
        comment_id: str,
        last_id: str | None = None,
        limit: int = 10,
        sort: Literal["asc", "desc"] = "desc",
    ) -> list[Comment]:
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
            {"$limit": limit},
        ]
        return [
            Comment(
                id=str(comment.get("_id")),
                text=comment.get("text"),
                author_id=comment.get("author_id"),
                author_name=comment.get("author_name"),
                author_email=comment.get("author_email"),
                author_photo_url=comment.get("author_photo_url"),
                parent_id=comment.get("parent_id"),
                post_id=comment.get("post_id"),
                dislikes=comment.get("dislikes"),
                likes=comment.get("likes"),
                answers_count=comment.get("answers_count"),
                created_at=datetime.fromisoformat(comment["created_at"]),
            )
            async for comment in self.db["comments"].aggregate(pipeline)
        ]

    async def create_answer(self, answer: Comment, comment_id: str) -> Comment:
        res = await self.db["comments"].insert_one(
            {
                "text": answer.text,
                "author_id": answer.author_id,
                "author_name": answer.author_name,
                "author_email": answer.author_email,
                "author_photo_url": answer.author_photo_url,
                "parent_id": comment_id,
                "post_id": answer.post_id,
                "dislikes": [],
                "likes": [],
                "answers_count": 0,
                "created_at": answer.created_at.isoformat(),
            }
        )
        await self.db["posts"].update_one(
            {"_id": ObjectId(answer.post_id)}, {"$inc": {"comments_count": 1}}
        )

        answer.id = str(res.inserted_id)
        return answer

    async def like_comment(self, comment_id: str, user_id: int) -> bool:
        res = await self.db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$addToSet": {"likes": user_id},
                "$pull": {"dislikes": user_id},
            },
        )
        return bool(res.modified_count)

    async def dislike_comment(self, comment_id: str, user_id: int) -> bool:
        res = await self.db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$addToSet": {"dislikes": user_id},
                "$pull": {"likes": user_id},
            },
        )
        return bool(res.modified_count)

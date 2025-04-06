from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Comment:
    id: str | None
    text: str
    author_id: int
    author_name: str
    author_email: str
    author_photo_url: str
    parent_id: str
    post_id: str
    dislikes: set[int]  # id's of users who disliked
    likes: set[int]  # id's of users who liked
    answers_count: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "author_photo_url": self.author_photo_url,
            "parent_id": self.parent_id,
            "post_id": self.post_id,
            "dislikes": self.dislikes,
            "likes": self.likes,
            "answers_count": self.answers_count,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Comment":
        return cls(
            id=data["id"],
            text=data["text"],
            author_id=data["author_id"],
            author_name=data["author_name"],
            author_email=data["author_email"],
            author_photo_url=data["author_photo_url"],
            parent_id=data["parent_id"],
            post_id=data["post_id"],
            dislikes=data["dislikes"],
            likes=data["likes"],
            answers_count=data["answers_count"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class Post:
    id: str
    title: str
    content: str
    author_id: int
    author_name: str
    author_email: str
    author_photo_url: str
    dislikes: set[int]  # ids of users that disliked this post
    likes: set[int]  # ids of users that liked this post
    created_at: datetime
    comments_count: int
    recent_comments: list[Comment]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "author_photo_url": self.author_photo_url,
            "dislikes": self.dislikes,
            "likes": self.likes,
            "created_at": self.created_at.isoformat(),
            "comments_count": self.comments_count,
            "recent_comments": [
                Comment.to_dict(comment) for comment in self.recent_comments
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Post":
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            author_id=data["author_id"],
            author_name=data["author_name"],
            author_email=data["author_email"],
            author_photo_url=data["author_photo_url"],
            dislikes=data["dislikes"],
            likes=data["likes"],
            created_at=datetime.fromisoformat(data["created_at"]),
            comments_count=data["comments_count"],
            recent_comments=data["recent_comments"],
        )

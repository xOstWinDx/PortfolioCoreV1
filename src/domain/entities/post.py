from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Author:
    id: int
    name: str
    email: str
    photo_url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "photo_url": self.photo_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Author":
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            photo_url=data["photo_url"],
        )


@dataclass
class Comment:
    id: str | None
    text: str
    author: Author | None
    parent_id: str | None
    post_id: str
    dislikes: set[int]  # id's of users who disliked
    likes: set[int]  # id's of users who liked
    answers_count: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        if not isinstance(self.author, Author):
            raise TypeError(f"Author must be of type Author, not {type(self.author)}")
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author.to_dict(),
            "parent_id": self.parent_id,
            "post_id": self.post_id,
            "dislikes": self.dislikes,
            "likes": self.likes,
            "answers_count": self.answers_count,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Comment":
        data["id"] = data.pop("_id", data.get("id"))
        return cls(
            id=str(data["id"]),
            text=data["text"],
            author=Author.from_dict(data["author"]),
            parent_id=str(data["parent_id"]),
            post_id=str(data["post_id"]),
            dislikes=data["dislikes"],
            likes=data["likes"],
            answers_count=data["answers_count"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class Post:
    id: str | None
    title: str
    content: str
    author: Author | None
    dislikes: set[int]  # ids of users that disliked this post
    likes: set[int]  # ids of users that liked this post
    created_at: datetime
    comments_count: int
    recent_comments: list[Comment]

    def to_dict(self) -> dict[str, Any]:
        if not isinstance(self.author, Author):
            raise TypeError(f"Author must be of type Author, not {type(self.author)}")
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author.to_dict(),
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
        data["id"] = data.pop("_id", data.get("id"))
        return cls(
            id=str(data["id"]),
            title=data["title"],
            content=data["content"],
            author=Author(**data["author"]),
            dislikes=data["dislikes"],
            likes=data["likes"],
            created_at=datetime.fromisoformat(data["created_at"]),
            comments_count=data["comments_count"],
            recent_comments=[
                Comment.from_dict(comment) for comment in data["recent_comments"]
            ],
        )

from dataclasses import dataclass
from typing import Any

from src.domain.entities.base import BaseEntity
from src.domain.entities.user import Author


@dataclass
class Project(BaseEntity):
    id: int
    title: str
    description: str
    tags: list[str]
    stack: list[str]
    author: Author | None

    def to_dict(self) -> dict[str, Any]:
        if not isinstance(self.author, Author):
            raise TypeError(f"Author must be of type Author, not {type(self.author)}")
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "stack": self.stack,
            "author": self.author.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            tags=data["tags"],
            stack=data["stack"],
            author=Author.from_dict(data["author"]),
            created_at=data["created_at"],
        )

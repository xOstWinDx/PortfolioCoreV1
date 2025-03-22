from sqlalchemy.orm import Mapped

from src.infrastructure.database import Str128
from src.infrastructure.models.base import Base


class ProjectModel(Base):
    __tablename__ = "projects"
    title: Mapped[Str128]
    description: Mapped[str]
    tags: Mapped[list]
    stack: Mapped[list]

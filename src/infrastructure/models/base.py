from datetime import datetime, UTC

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), server_default=func.now()
    )

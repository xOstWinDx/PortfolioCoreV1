from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseEntity:
    id: int | None
    created_at: datetime

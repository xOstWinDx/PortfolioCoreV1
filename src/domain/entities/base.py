from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseEntity:
    id: int
    created_at: datetime

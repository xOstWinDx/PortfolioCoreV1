from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseFilter:
    id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

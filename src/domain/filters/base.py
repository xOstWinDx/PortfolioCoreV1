from dataclasses import dataclass
from typing import Any

from src.domain.utils import safe_as_dict


@dataclass
class BaseFilter:
    id: int | None = None

    def to_dict(self, exclude_none: bool = False) -> dict[str, Any]:
        res = safe_as_dict(self)
        if not exclude_none:
            return res
        return {k: v for k, v in res.items() if v is not None}

from dataclasses import is_dataclass, asdict
from typing import TypeVar, Any

T = TypeVar("T")


def safe_as_dict(obj: T) -> dict[str, Any]:
    assert is_dataclass(obj), "Объект должен быть дата-классом"
    return asdict(obj)  # type: ignore

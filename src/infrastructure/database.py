from typing import Annotated

from sqlalchemy import String
from sqlalchemy.orm import mapped_column

Str128 = Annotated[str, mapped_column(String(128))]
Str16 = Annotated[str, mapped_column(String(16))]

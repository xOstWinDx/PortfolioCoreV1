from typing import Protocol


class Credentials(Protocol):
    def get_raw_data(self) -> dict[str, str]:
        pass

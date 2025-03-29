from typing import Protocol


class Credentials(Protocol):
    def get_authorize(self) -> str:
        """Получить данные для предоставления прав доступа."""
        pass

    def get_authenticate(self) -> str:
        """Получить данные для подтверждения личности."""
        pass

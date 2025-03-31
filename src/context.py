from src.application.interfaces.credentials import Credentials


class CredentialsHolder:
    def __init__(self) -> None:
        self.credentials: Credentials | None = None

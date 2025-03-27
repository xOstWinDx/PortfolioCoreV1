class UserAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User with email {email} already exists")

    def __repr__(self) -> str:
        return f"User with email {self.email} already exists"


class TokenError(Exception):
    def __init__(self) -> None:
        super().__init__("Invalid token")

    def __repr__(self) -> str:
        return "Invalid token"


class AuthError(Exception):
    def __init__(self) -> None:
        super().__init__("Email or Password is incorrect")

    def __repr__(self) -> str:
        return "Email or Password is incorrect"

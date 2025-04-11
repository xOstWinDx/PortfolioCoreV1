from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, EmailStr, field_validator


class LoginUserSchema(BaseModel):
    email: Annotated[EmailStr, Form()]
    password: Annotated[str, Form()]


class RegisterUserSchema(LoginUserSchema):
    username: Annotated[str, Form()]

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        return value


class Author(BaseModel):
    id: int
    name: str
    email: str
    photo_url: str

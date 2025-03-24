from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from starlette import status
from starlette.requests import Request

from src.application.interfaces.services.auth import AbstractAuthService
from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.container import Container
from src.domain.entities.tokens import TokenType, RefreshTokenPayload, RefreshToken

container = Container()


async def get_login_use_case() -> LoginUseCase:
    use_case: LoginUseCase = container.login_use_case()
    return use_case


async def get_auth_service() -> AbstractAuthService:
    auth_service: AbstractAuthService = container.auth_service()
    return auth_service


async def get_update_token_use_case() -> UpdateTokenUseCase:
    use_case: UpdateTokenUseCase = container.update_token_use_case()
    return use_case


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


class RefreshTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        # 1. Проверяем куки в первую очередь
        if "refresh_token" in request.cookies:
            return request.cookies["refresh_token"]  # type: ignore

        # 2. Если нет в куках, проверяем заголовки
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )
            return credentials.credentials  # type: ignore

        return None


refresh_token_bearer = RefreshTokenBearer()


async def validate_refresh_token(
    token: Annotated[str, Depends(refresh_token_bearer)],
    auth_service: AbstractAuthService = Depends(get_auth_service),
) -> RefreshToken:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing"
        )

    # Проверяем, что это именно refresh token
    payload = auth_service.decode_token(token)
    if not payload or payload.type != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    if not isinstance(payload, RefreshTokenPayload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    return RefreshToken(token=token, payload=payload)

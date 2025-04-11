from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from starlette.requests import Request

from src.container import container
from src.context import CredentialsHolder


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        # 1. Проверяем куки в первую очередь
        if "access_token" in request.cookies:
            return request.cookies["access_token"]  # type: ignore

        # 2. Если нет в куках, проверяем заголовки
        credentials = await HTTPBearer.__call__(self, request)
        if credentials:
            if credentials.scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )
            return credentials.credentials  # type: ignore

        return None


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


class CredentialsBearer(AccessTokenBearer, RefreshTokenBearer):
    async def __call__(self, request: Request) -> str | None:
        access = await AccessTokenBearer.__call__(self, request)
        refresh = await RefreshTokenBearer.__call__(self, request)
        creds = container.credentials(authorize=access, authenticate=refresh)
        return creds  # type: ignore


credentials_schema = CredentialsBearer(auto_error=False)


async def get_creds_holder(request: Request) -> CredentialsHolder:
    if hasattr(request.state, "creds_holder"):
        return request.state.creds_holder  # type: ignore
    request.state.creds_holder = CredentialsHolder()
    return request.state.creds_holder

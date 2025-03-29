from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status
from starlette.requests import Request


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> str | None:
        # 1. Проверяем куки в первую очередь
        if "access_token" in request.cookies:
            return request.cookies["access_token"]  # type: ignore

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


access_token_schema = AccessTokenBearer()

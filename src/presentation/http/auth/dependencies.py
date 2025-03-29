from fastapi import HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from starlette import status
from starlette.requests import Request


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

# async def validate_refresh_token(
#     token: Annotated[str, Depends(refresh_token_bearer)],
#     auth_service: AbstractAuthService = Depends(get_auth_service),
# ) -> RefreshToken:
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing"
#         )
#
#     # Проверяем, что это именно refresh token
#     payload = auth_service.decode_token(token)
#     if not payload or payload.type != TokenType.REFRESH:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
#         )
#     if not isinstance(payload, RefreshTokenPayload):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
#         )
#     return RefreshToken(token=token, payload=payload)

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.sql.annotation import Annotated
from starlette.requests import Request

from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.container import Container

container = Container()


async def get_login_use_case() -> LoginUseCase:
    use_case: LoginUseCase = container.login_use_case()
    return use_case


async def get_update_token_use_case() -> UpdateTokenUseCase:
    use_case: UpdateTokenUseCase = container.update_token_use_case()
    return use_case


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# async def auth_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> str:
#     token = token or request.cookies.get("access_token")
#     if token is None:
#         return None


async def get_refresh_token(
    request: Request, refresh_token: Annotated[str, Depends(oauth2_scheme)]
) -> str | None:
    token: str | None = refresh_token or request.cookies.get("refresh_token")
    if token is None:
        return None
    auth = container.auth_service()
    payload = auth.decode_token(token)
    if not payload:
        return None

    return token

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse
from user_agents import parse

from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.domain.entities.tokens import RefreshToken
from src.presentation.http.auth.dependencies import (
    get_login_use_case,
    get_update_token_use_case,
    validate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(  # type: ignore
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[LoginUseCase, Depends(get_login_use_case)],
):
    # Извлекаем User-Agent из заголовков
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)

    # Определяем платформу и браузер
    platform = user_agent.os.family  # Например, "Windows", "iOS", "Android"
    browser = user_agent.browser.family  # Например, "Chrome", "Firefox", "Safari"

    tokens = await use_case(
        username=form_data.username,
        password=form_data.password,
        ip=request.client.host,
        platform=platform,
        browser=browser,
    )
    if tokens is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    response = JSONResponse(
        content={"access_token": tokens[0], "refresh_token": tokens[1]}
    )
    response.set_cookie(
        key="refresh_token", value=tokens[1], httponly=True, secure=True
    )
    response.set_cookie(
        key="access_token",
        value=tokens[0],
        httponly=True,
    )
    return response


@router.post("/update_token")
async def update_token(  # type: ignore
    request: Request,
    use_case: Annotated[UpdateTokenUseCase, Depends(get_update_token_use_case)],
    refresh_token: Annotated[RefreshToken, Depends(validate_refresh_token)],
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    # Извлекаем User-Agent из заголовков
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)

    # Определяем платформу и браузер
    platform = user_agent.os.family  # Например, "Windows", "iOS", "Android"
    browser = user_agent.browser.family  # Например, "Chrome", "Firefox", "Safari"
    token = await use_case(
        ip=request.client.host,
        platform=platform,
        browser=browser,
        refresh_token=refresh_token.token,
    )
    if token is None:
        # Удаляем куку "token"
        headers = {"Set-Cookie": "refresh_token=;"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect refresh token",
            headers=headers,
        )
    response = JSONResponse(content={"access_token": token})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
    )
    return response

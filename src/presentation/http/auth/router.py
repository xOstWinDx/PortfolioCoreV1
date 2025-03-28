from typing import Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse
from user_agents import parse

from src.application.usecases.login import LoginUseCase
from src.application.usecases.update_token import UpdateTokenUseCase
from src.container import container
from src.domain.entities.tokens import RefreshToken
from src.domain.exceptions.auth import TokenError
from src.presentation.http.auth.dependencies import (
    get_update_token_use_case,
)

router = APIRouter(prefix="/auth", tags=["auth"])

container.wire(modules=[__name__])


@router.post("/register")
@inject
async def register() -> (
    None
):  # TODO: сделать форму для регистрации с Email (наследник нижней)
    pass


@router.post("/login")
@inject
async def login(  # type: ignore
    request: Request,
    form_data: Annotated[..., Depends()],  # TODO: сделать схему для входа с Email
    use_case: Annotated[LoginUseCase, Provide[container.login_use_case]],
):
    # Извлекаем User-Agent из заголовков
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)

    # Определяем платформу и браузер
    platform = user_agent.os.family  # Например, "Windows", "iOS", "Android"
    browser = user_agent.browser.family  # Например, "Chrome", "Firefox", "Safari"

    tokens = await use_case(
        email=form_data.username,
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
        key="access_token",
        value=tokens[0],
        httponly=True,
    )
    response.set_cookie(
        key="refresh_token", value=tokens[1], httponly=True, secure=True
    )
    return response


@router.post("/update_token")
@inject
async def update_token(  # type: ignore
    request: Request,
    use_case: Annotated[UpdateTokenUseCase, Depends(get_update_token_use_case)],
    refresh_token: Annotated[RefreshToken, Provide[container.update_token_use_case]],
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    # Извлекаем User-Agent из заголовков
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)

    # Определяем платформу и браузер
    platform = user_agent.os.family  # Например, "Windows", "iOS", "Android"
    browser = user_agent.browser.family  # Например, "Chrome", "Firefox", "Safari"
    try:
        token = await use_case(
            ip=request.client.host,
            platform=platform,
            browser=browser,
            refresh_token=refresh_token.token,
        )
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.msg)

    response = JSONResponse(content={"access_token": token})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
    )
    return response

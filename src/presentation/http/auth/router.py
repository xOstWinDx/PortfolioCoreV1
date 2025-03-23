from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from user_agents import parse

from src.application.usecases.login import LoginUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def get_token(  # type: ignore
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[LoginUseCase, Depends()],
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

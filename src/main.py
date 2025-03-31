from typing import Awaitable, Callable

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from src.config import CONFIG
from src.context import CredentialsHolder
from src.presentation.http.auth.router import router as auth_router
from src.presentation.http.projects.router import router as projects_router

app = FastAPI(
    title="Portfolio Backend",
    version="0.0.1",
    description="API for my portfolio website and blog.",
)

app.include_router(projects_router)
app.include_router(auth_router)


@app.middleware("http")
async def credentials_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    creds_holder = CredentialsHolder()  # Ящик для новый кредов.
    request.state.creds_holder = creds_holder
    response: Response = await call_next(request)
    creds = request.state.creds_holder.credentials
    if creds:
        response.set_cookie(
            "access_token",
            creds.get_authorize(),
            httponly=True,
            max_age=CONFIG.ACCESS_TOKEN_EXPIRE_SECONDS,
        )
    return response


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World!"}

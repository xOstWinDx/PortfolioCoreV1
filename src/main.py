from time import time
from typing import Awaitable, Callable

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from redis.asyncio import Redis
from starlette.requests import Request
from starlette.responses import Response

from src.config import CONFIG
from src.container import Container
from src.context import CredentialsHolder
from src.presentation.http.auth.router import router as auth_router
from src.presentation.http.projects.router import router as projects_router

container = Container()

app = FastAPI(
    title="Portfolio Backend",
    version="0.0.1",
    description="API for my portfolio website and blog.",
)

app.include_router(projects_router)
app.include_router(auth_router)


@app.middleware("http")
async def credentials_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
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
        response.set_cookie(
            "refresh_token",
            creds.get_authenticate(),
            httponly=True,
            max_age=CONFIG.REFRESH_TOKEN_EXPIRE_SECONDS,
            secure=True,
        )
    return response


@app.middleware("http")
@inject
async def rate_limit_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
    redis: Redis = Provide["redis"],
) -> Response:
    """Базовая реализация лимитирования запросов через алгоритм Фиксированного окна."""
    async with redis:
        async with redis.pipeline(transaction=True) as pipe:
            key = f"rate_limit:{request.client.host}"
            await pipe.exists(key)
            await pipe.get(key)
            await pipe.ttl(key)
            exist, count, ttl = await pipe.execute()
            count = int(count) if count is not None else CONFIG.RATE_LIMIT_LIMIT
            if exist:
                if count <= 0:
                    return Response(
                        status_code=429,
                        headers={
                            "X-Rate-Limit": str(CONFIG.RATE_LIMIT_LIMIT),
                            "X-Rate-Limit-Remaining": "0",
                            "X-Rate-Limit-Reset": str(int(time() + ttl)),
                            "Retry-After": str(ttl),
                        },
                    )
                await pipe.decr(key)
                await pipe.execute()
            else:
                await pipe.set(
                    key,
                    CONFIG.RATE_LIMIT_LIMIT - 1,
                    ex=CONFIG.RATE_LIMIT_EXPIRE_SECONDS,
                )
                await pipe.execute()

    response = await call_next(request)
    response.headers["X-Rate-Limit"] = str(CONFIG.RATE_LIMIT_LIMIT)
    response.headers["X-Rate-Limit-Remaining"] = (
        str(count - 1) if count else CONFIG.RATE_LIMIT_LIMIT
    )
    response.headers["X-Rate-Limit-Reset"] = str(
        int(time() + ttl if ttl else CONFIG.RATE_LIMIT_EXPIRE_SECONDS)
    )
    return response


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World!"}


container.wire(modules=[__name__])

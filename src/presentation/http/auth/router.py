from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from src.application.interfaces.credentials import Credentials
from src.application.usecases.login import LoginUseCase
from src.application.usecases.register_user import RegisterUserUseCase
from src.application.usecases.update_token import UpdateCredentialsUseCase
from src.container import Container
from src.domain.exceptions.auth import TokenError, UserAlreadyExistsError, AuthError
from src.infrastructure.schemas.user import LoginUserSchema, RegisterUserSchema
from src.presentation.http.auth.dependencies import refresh_token_bearer
from src.presentation.http.dependencies import credentials_schema

router = APIRouter(prefix="/auth", tags=["auth"])

container = Container()


@router.post("/register", status_code=201)
async def register(
    form_data: RegisterUserSchema,
    use_case: RegisterUserUseCase = Depends(lambda: container.register_use_case()),
) -> dict[str, str]:
    try:
        await use_case(
            username=form_data.username,
            email=str(form_data.email),
            password=form_data.password,
        )
        return {"message": "User registered successfully"}
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


@router.post("/login", status_code=200)
async def login(  # type: ignore
    form_data: LoginUserSchema,
    use_case: LoginUseCase = Depends(lambda: container.login_use_case()),
    credentials: Credentials = Depends(credentials_schema),
):
    try:
        creds = await use_case(
            credentials=credentials,
            email=str(form_data.email),
            password=form_data.password,
        )
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    response = JSONResponse(
        content={
            "access_token": creds.get_authorize(),
            "refresh_token": creds.get_authenticate(),
        }
    )
    response.set_cookie(
        key="access_token",
        value=creds.get_authorize(),
        httponly=True,
    )
    response.set_cookie(
        key="refresh_token", value=creds.get_authenticate(), httponly=True, secure=True
    )
    return response


@router.post("/update_token", status_code=200)
async def update_token(  # type: ignore
    refresh_token: Annotated[str, Depends(refresh_token_bearer)],
    use_case: UpdateCredentialsUseCase = Depends(
        lambda: container.update_token_use_case()
    ),
):
    try:
        creds = await use_case(
            credentials=container.credentials(
                access_token="",
                refresh_token=refresh_token,
            )
        )
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.msg)

    response = JSONResponse(content={"access_token": creds.get_authorize()})
    response.set_cookie(
        key="access_token",
        value=creds.get_authorize(),
        httponly=True,
    )
    return response


container.wire(modules=[__name__])  # должен быть внизу.

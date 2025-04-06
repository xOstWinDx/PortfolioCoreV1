from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.application.authorize import UseCaseGuard
from src.application.interfaces.credentials import Credentials
from src.application.usecases.users.login import LoginUseCase
from src.application.usecases.users.register_user import RegisterUserUseCase
from src.container import Container
from src.context import CredentialsHolder
from src.domain.exceptions.auth import UserAlreadyExistsError, AuthError
from src.domain.value_objects.auth import AuthorizationContext  # noqa: F401
from src.infrastructure.schemas.user import LoginUserSchema, RegisterUserSchema
from src.presentation.http.dependencies import credentials_schema, get_creds_holder

router = APIRouter(prefix="/auth", tags=["auth"])

container = Container()


@router.post("/register", status_code=201)
@inject
async def register(
    form_data: RegisterUserSchema,
    request: Request,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    credentials: Credentials = Depends(credentials_schema),
    guard: UseCaseGuard[RegisterUserUseCase] = Depends(Provide["register_use_case"]),
) -> dict[str, str | int | None]:
    try:
        guard.configure(
            credentials=credentials,
            creds_holder=creds_holder,
            device_id=str(request.client.host),
        )
        async with guard as (use_case, _, _):  # type: RegisterUserUseCase # type: ignore[no-redef]
            user = await use_case(
                username=form_data.username,
                email=str(form_data.email),
                password=form_data.password,
            )
            return {"message": "User registered successfully", "user_id": user.id}
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )


@router.post("/login", status_code=200)
async def login(  # type: ignore
    form_data: LoginUserSchema,
    request: Request,
    creds_holder: CredentialsHolder = Depends(get_creds_holder),
    guard: UseCaseGuard[LoginUseCase] = Depends(lambda: container.login_use_case()),
    credentials: Credentials = Depends(credentials_schema),
):
    try:
        guard.configure(
            credentials=credentials,
            creds_holder=creds_holder,
            device_id=str(request.client.host),
        )
        async with guard as (use_case, _, _):  # type: LoginUseCase # type: ignore[no-redef]
            creds = await use_case(
                credentials=credentials,
                email=str(form_data.email),
                password=form_data.password,
                device_id=str(request.client.host),
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


# @router.post("/update_token", status_code=200)
# async def update_token(  # type: ignore
#     refresh_token: Annotated[str, Depends(refresh_token_bearer)],
#     use_case: UpdateCredentialsUseCase = Depends(
#         lambda: container.update_token_use_case()
#     ),
# ):
#     try:
#         creds = await use_case(
#             credentials=container.credentials(
#                 access_token="",
#                 refresh_token=refresh_token,
#             )
#         )
#     except TokenError as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.msg)
#
#     response = JSONResponse(content={"access_token": creds.get_authorize()})
#     response.set_cookie(
#         key="access_token",
#         value=creds.get_authorize(),
#         httponly=True,
#     )
#     return response


container.wire(modules=[__name__])  # должен быть внизу.

from src.application.usecases.login import LoginUseCase
from src.container import Container

container = Container()


async def get_login_use_case() -> LoginUseCase:
    use_case: LoginUseCase = container.login_use_case()
    return use_case

from functools import partial

from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.application.authorize import UseCaseGuard
from src.application.services.posts import PostsService
from src.application.usecases.posts.comments.answers.create import CreateAnswerUseCase
from src.application.usecases.posts.comments.answers.get import GetAnswersUseCase
from src.application.usecases.posts.comments.create import CreateCommentUseCase
from src.application.usecases.posts.comments.get import GetCommentsUseCase
from src.application.usecases.posts.comments.rate import RateCommentUseCase
from src.application.usecases.posts.create import CreatePostUseCase
from src.application.usecases.posts.get import GetPostsUseCase
from src.application.usecases.posts.rate import RatePostUseCase
from src.application.usecases.projects.add_project import CreateProjectUseCase
from src.application.usecases.users.login import LoginUseCase
from src.application.usecases.users.register_user import RegisterUserUseCase
from src.config import CONFIG
from src.domain.entities.user import RolesEnum
from src.domain.value_objects.auth import AuthorizationContext
from src.infrastructure.clients.cache import RedisCacheClient
from src.infrastructure.credentials import JwtCredentials
from src.infrastructure.repositories.tokens import JWTRedisAuthRepository
from src.infrastructure.services.auth import JwtAuthService
from src.infrastructure.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    # region Base depends

    mongo_factory = partial(
        AsyncIOMotorClient,
        CONFIG.MONGO_URL,
    )

    engine = providers.Singleton(create_async_engine, url=CONFIG.DATABASE_URL)

    session_factory = providers.Singleton(
        async_sessionmaker, bind=engine, expire_on_commit=False
    )
    redis_pool = providers.Singleton(
        ConnectionPool.from_url,
        url=CONFIG.DEV_REDIS_URL,
        decode_responses=True,
    )

    redis = providers.Singleton(  # Ресурс провайдер обеспечивает открытие и закрытие соединения
        Redis,
        connection_pool=redis_pool,
    )
    auth_repo = providers.Factory(JWTRedisAuthRepository, redis_client=redis)
    auth_service = providers.Factory(JwtAuthService, auth_repo=auth_repo)
    cache_client = providers.Singleton(RedisCacheClient, redis_client=redis)

    uow = providers.Factory(
        UnitOfWork,
        sql_session_factory=session_factory,
        mongo_client_factory=mongo_factory,
    )
    posts = providers.Factory(PostsService, uow=uow, cache_client=cache_client)

    # endregion

    # region Credentials
    credentials = providers.Factory(
        JwtCredentials,
        authorize=providers.Callable(str),
        authenticate=providers.Callable(str),
    )

    default_context = providers.Singleton(
        AuthorizationContext,
        user_id=None,
        role=RolesEnum.GUEST,
    )
    # endregion

    # region Use cases without auth
    _register_use_case = providers.Factory(
        RegisterUserUseCase,
        uow=uow,
        auth=auth_service,
    )
    _login_use_case = providers.Factory(
        LoginUseCase,
        uow=uow,
        auth=auth_service,
    )
    _create_project_use_case = providers.Factory(
        CreateProjectUseCase,
        uow=uow,
        auth=auth_service,
    )

    _create_post_use_case = providers.Factory(
        CreatePostUseCase, uow=uow, auth=auth_service, posts=posts
    )
    _get_posts_use_case = providers.Factory(
        GetPostsUseCase, uow=uow, auth=auth_service, posts=posts
    )
    _rate_post_use_case = providers.Factory(
        RatePostUseCase,
        uow=uow,
        auth=auth_service,
        posts=posts,
    )
    _create_comment_use_case = providers.Factory(
        CreateCommentUseCase,
        uow=uow,
        auth=auth_service,
        posts=posts,
    )
    _get_comments_use_case = providers.Factory(
        GetCommentsUseCase,
        uow=uow,
        auth=auth_service,
        posts=posts,
    )
    _create_answer_use_case = providers.Factory(
        CreateAnswerUseCase, uow=uow, auth=auth_service, posts=posts
    )
    _get_answers_use_case = providers.Factory(
        GetAnswersUseCase, uow=uow, auth=auth_service, posts=posts
    )
    _rate_comment_use_case = providers.Factory(
        RateCommentUseCase, uow=uow, auth=auth_service, posts=posts
    )
    # endregion

    # region Use cases with auth
    register_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_register_use_case,
        uow=uow,
        default_context=default_context,
    )
    login_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_login_use_case,
        uow=uow,
        default_context=default_context,
    )
    create_project_use_case: CreateProjectUseCase = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.ADMIN,
        auth_service=auth_service,
        use_case=_create_project_use_case,
        uow=uow,
        default_context=default_context,
    )
    create_post_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.ADMIN,
        auth_service=auth_service,
        use_case=_create_post_use_case,
        uow=uow,
        default_context=default_context,
    )
    get_posts_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_get_posts_use_case,
        uow=uow,
        default_context=default_context,
    )
    rate_post_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.USER,
        auth_service=auth_service,
        use_case=_rate_post_use_case,
        uow=uow,
        default_context=default_context,
    )
    create_comment_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.USER,
        auth_service=auth_service,
        use_case=_create_comment_use_case,
        uow=uow,
        default_context=default_context,
    )
    get_comments_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_get_comments_use_case,
        uow=uow,
        default_context=default_context,
    )
    create_answer_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.USER,
        auth_service=auth_service,
        use_case=_create_answer_use_case,
        uow=uow,
        default_context=default_context,
    )
    get_answers_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.GUEST,
        auth_service=auth_service,
        use_case=_get_answers_use_case,
        uow=uow,
        default_context=default_context,
    )
    rate_comment_use_case = providers.Factory(
        UseCaseGuard,
        required_role=RolesEnum.USER,
        auth_service=auth_service,
        use_case=_rate_comment_use_case,
        uow=uow,
        default_context=default_context,
    )
    # endregion


container = Container()

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from app.exceptions.routes.models import ForbiddenError
from app.utils.decorators import standardize_response
from app.v1.schemas.responses import BaseResponse
from app.v1.security.auth import GetCurrentUser
from app.v1.security.utils import Permission
from app.v1.users.dependencies import UsersDependencyMarker
from app.v1.users.schemas import CreateUserModel
from app.v1.users.schemas import GetCurrentUserModel
from app.v1.users.schemas import GetUserWithPhoneEmail
from app.v1.users.schemas import RegisterUserDTO
from app.v1.users.schemas import UpdateActivityDTO
from app.v1.users.schemas import UpdateMeDTO
from app.v1.users.services import UserService

user_router = APIRouter()


@user_router.post(
    "/auth/register",
    summary="Создание пользователя",
    response_model=BaseResponse[RegisterUserDTO],
    status_code=200,
)
@standardize_response(status_code=200)
async def create_user(
    data: CreateUserModel,
    user_service: UserService = Depends(UsersDependencyMarker),
):
    user = await user_service.create(
        phone=data.phone,
        first_name=data.first_name,
        last_name=data.last_name,
        login=data.login,
        password=data.password,
        status_id=3,
    )
    return user


@user_router.get(
    "/users/{uuid}",
    summary="Получение пользователя",
    response_model=BaseResponse[GetUserWithPhoneEmail],
    status_code=200,
)
@standardize_response(status_code=200)
async def get_user(
    uuid: UUID,
    current_user: GetCurrentUserModel = Depends(GetCurrentUser()),
    user_service: UserService = Depends(UsersDependencyMarker),
):
    user = await user_service.get_one_from_uuid(uuid=uuid, author_uuid=current_user.uuid)

    if user.role.id not in Permission.PROFILE_GET.get(current_user.role.id):
        raise ForbiddenError("У вас нет прав на просмотр данного профиля")

    return user


@user_router.get(
    "/users",
    summary="Получение пользователей",
    response_model=BaseResponse[list[GetUserWithPhoneEmail]],
    status_code=200,
)
@standardize_response(status_code=200)
async def get_user(
    current_user: GetCurrentUserModel = Depends(GetCurrentUser()),
    user_service: UserService = Depends(UsersDependencyMarker),
):
    user = await user_service.get_all(author_uuid=current_user.uuid)
    return user


@user_router.patch(
    "/auth/me/activity",
    summary="Обновить последнюю активность",
    # response_model=BaseResponse[list[GetUserWithPhoneEmail]],
    status_code=200,
    include_in_schema=True,
)
@standardize_response(status_code=200)
async def update_last_activity(
    data: UpdateActivityDTO,
    current_user: GetCurrentUserModel = Depends(GetCurrentUser()),
    user_service: UserService = Depends(UsersDependencyMarker),
):
    user = await user_service.update_activity(uuid=current_user.uuid, data=data)
    return user


@user_router.patch(
    "/auth/me",
    summary="Обновить данные",
    response_model=BaseResponse[RegisterUserDTO],
    status_code=200,
    include_in_schema=True,
)
@standardize_response(status_code=200)
async def update_me(
    data: UpdateMeDTO,
    current_user: GetCurrentUserModel = Depends(GetCurrentUser()),
    user_service: UserService = Depends(UsersDependencyMarker),
):
    user = await user_service.update_me(uuid=current_user.uuid, data=data)
    return user

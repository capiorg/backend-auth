import datetime
from enum import Enum
from typing import Any
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from pydantic import Field
from pydantic import validator

from app.dto.types.datetime_without_tz import DateTimeWithoutTZ
from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.phone import Phone
from app.v1.statuses.schemas import StatusGetMixinV3


class RoleEnum(int, Enum):
    ADMIN = 1
    MODERATOR = 2
    USER = 3


class RoleDTO(BaseModelORM):
    id: int
    title: str


class AvatarDTO(BaseModelORM):
    document_id: UUID
    url: Optional[str] = None

    @validator("url", always=True, check_fields=False)
    def validate_avatar(cls, _: str, values: dict[Any, Any]):
        avatar_id = values.get("document_id")
        return f"https://document.capi.shitposting.team/v1/documents/{avatar_id}/file"


class GetUserModel(BaseModelORM):
    uuid: UUID
    login: str
    first_name: str
    last_name: str
    login_at: Optional[str] = None
    is_me: Optional[bool] = True

    avatar: Optional[AvatarDTO] = None
    role: Optional[RoleDTO] = None

    is_online: bool
    last_activity: Optional[datetime.datetime]

    @validator("login_at", always=True, check_fields=False)
    def validate_login(cls, _: str, values: dict[Any, Any]):
        login = values.get("login")
        return f"@{login}"


class GetUserWithPhoneEmail(GetUserModel):
    phone: str
    email: Optional[EmailStr] = None


class GetCurrentUserModel(GetUserWithPhoneEmail):
    session_id: Optional[UUID] = None


class GetUserWithStatus(GetUserModel, StatusGetMixinV3):
    pass


class CreateUserModel(BaseModelORM):
    login: str
    phone: Phone
    password: str
    first_name: str
    last_name: str


class UpdateActivityDTO(BaseModelORM):
    is_online: bool
    last_activity: Optional[DateTimeWithoutTZ]


class UpdateMeDTO(BaseModelORM):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    avatar_id: Optional[UUID] = None


class RegisterUserDTO(BaseModelORM):
    uuid: UUID
    login: str
    first_name: str
    last_name: str

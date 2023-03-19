from typing import Type

from app.v1.users.schemas import RoleEnum


class Permission:
    PROFILE_GET = {
        RoleEnum.USER: [RoleEnum.USER],
        RoleEnum.MODERATOR: [RoleEnum.USER, RoleEnum.MODERATOR],
        RoleEnum.ADMIN: [RoleEnum.USER, RoleEnum.MODERATOR, RoleEnum.USER]
    }

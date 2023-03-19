from typing import Any
from uuid import UUID

from sqlalchemy.orm import sessionmaker

from app.db.models import User
from app.v1.security.context import get_password_hash
from app.v1.users.repo import UserRepository
from app.v1.users.schemas import UpdateActivityDTO
from app.v1.users.schemas import UpdateMeDTO
from misc import cache


class UserService(UserRepository):
    def __init__(self, db_session: sessionmaker):
        super().__init__(db_session=db_session)

    async def create(
        self,
        login: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
        status_id: int,
    ) -> User:
        hashed_password = get_password_hash(password)
        return await super()._create(
            login=login,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            status_id=status_id,
            avatar_id=UUID("c4af61d6-64a0-4c34-891d-340977bbc2b3"),
            role_id=3,
        )

    async def update_activity(
        self,
        uuid: UUID,
        data: UpdateActivityDTO,
    ):
        data_without_none = data.dict(exclude_none=True)

        return await super()._update(
            uuid=uuid,
            **data_without_none,
        )

    @cache.invalidate("v2:users:get_current:user_uuid:{uuid}:*")
    async def update_me(
        self,
        uuid: UUID,
        data: UpdateMeDTO,
    ):
        if data.password:
            data.password = get_password_hash(data.password)

        if data.avatar_id:
            document = await self.create_document(document_id=data.avatar_id)
            data.avatar_id = document.uuid

        data_without_none = data.dict(exclude_none=True)

        return await super()._update(
            uuid=uuid,
            **data_without_none,
        )

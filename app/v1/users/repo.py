from typing import List
from uuid import UUID

from sqlalchemy import case
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import with_expression

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import Document
from app.db.models import User


class UserRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = User

        self.base = BaseCRUD(db_session=db_session, model=self.model)

    @orm_error_handler
    async def _create(
        self,
        login: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
        status_id: int,
        avatar_id: UUID,
        role_id: int,
    ) -> User:
        async with self.base.transaction_v2() as transaction:
            model = User(
                login=login,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                password=password,
                status_id=status_id,
                avatar_id=avatar_id,
                role_id=role_id,
            )
            transaction.add(model)
            await transaction.commit()
            return model

    @orm_error_handler
    async def _update(
        self,
        uuid: UUID,
        **kwargs,
    ):
        async with self.base.transaction_v2() as transaction:
            return await self.base.update(
                User.uuid == uuid,
                **kwargs,
            )

    @orm_error_handler
    async def create_document(self, document_id: UUID) -> Document:

        async with self.base.transaction_v2() as transaction:
            model = Document(
                document_id=document_id,
            )
            transaction.add(model)
            await transaction.commit()
            return model

    @orm_error_handler
    async def get_one_from_uuid(self, uuid: UUID, author_uuid: UUID) -> User:
        async with self.base.transaction_v2():
            stmt = (
                select(User)
                .options(
                    with_expression(
                        self.model.is_me,
                        self.__is_me_expression(user_id=author_uuid)
                    ),
                    joinedload(User.avatar),
                    joinedload(User.role),
                )
                .filter(User.uuid == uuid)
            )
            curr = await self.base.session.execute(stmt)
            return curr.scalar_one()

    @orm_error_handler
    async def get_one_from_phone(self, phone: str) -> User:
        async with self.base.transaction_v2():
            return await self.base.get_one(self.model.phone == phone)

    @orm_error_handler
    async def get_all(self, author_uuid: UUID) -> List[User]:
        async with self.base.transaction_v2():
            stmt = (
                select(User)
                .options(
                    with_expression(
                        self.model.is_me,
                        self.__is_me_expression(user_id=author_uuid)
                    ),
                    joinedload(self.model.role),
                    joinedload(self.model.avatar),
                )
            )
            curr = await self.base.session.execute(stmt)
            return curr.scalars().all()

    @orm_error_handler
    async def activate(self, uuid: UUID) -> User:
        async with self.base.transaction_v2() as transaction:
            result = await self.base.update(self.model.uuid == uuid, status_id=1)
            await transaction.commit()
            return result

    def __is_me_expression(self, user_id: UUID):
        return case(
            [(self.model.uuid == user_id, True)], else_=False
        ).label("is_me")

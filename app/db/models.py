import enum

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp
from uuid_extensions import uuid7

from app.db.mixins import TimestampMixin
from misc import Base


class SessionTypeEnum(str, enum.Enum):
    REGISTER = "REGISTER"
    AUTH = "AUTH"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)


class Statuses(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)


class Document(
    TimestampMixin,
    Base,
):
    __tablename__ = "documents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    document_id = Column(UUID(as_uuid=True))
    filename = Column(Text, nullable=True)
    size_bytes = Column(Numeric, nullable=True)
    mime_type = Column(String(255), nullable=True)


class StatusMixin(Base):
    __abstract__ = True

    @declared_attr
    def status_id(cls):
        return Column(Integer, ForeignKey(column=Statuses.id), default=1, nullable=True)

    @declared_attr
    def status(cls):
        return relationship(argument="Statuses", viewonly=True, lazy="joined")


class User(TimestampMixin, StatusMixin, Base):
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    phone = Column(String(20), index=True, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=True)
    login = Column(String, nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password = Column(String)

    avatar_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.uuid")
    )

    is_online = Column(Boolean, default=False)
    last_activity = Column(DateTime, default=current_timestamp())
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    avatar = relationship(
        "Document",
        lazy="joined"
    )
    role = relationship(
        "Role",
    )
    is_me = query_expression()


class SessionDevice(Base):
    __tablename__ = "sessions_devices"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)

    device_type = Column(String, nullable=True)
    device_brand = Column(String, nullable=True)
    device_family = Column(String, nullable=True)

    os_family = Column(String, nullable=True)
    os_version = Column(String, nullable=True)

    browser_family = Column(String, nullable=True)
    browser_version = Column(String, nullable=True)

    ip = Column(String)
    country = Column(String)
    city = Column(String)


class UserSession(StatusMixin, Base):
    __tablename__ = "users_sessions"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True)
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions_devices.uuid"),
        primary_key=True,
    )
    code = Column(String(length=4))
    session_type = Column(Enum(SessionTypeEnum), nullable=False)
    status_id = Column(Integer, ForeignKey(column=Statuses.id), default=3)

    device = relationship("SessionDevice")

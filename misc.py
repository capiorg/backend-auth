import sqlalchemy
from cashews import Cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.db.asyncpg_utils import *  # noqa
from config import settings_app
from config import settings_redis

DATABASE_URL = settings_app.dsn

engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    connect_args={"timeout": 30},
    pool_size=100,
)

async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)


cache = Cache()
cache.setup(
    settings_redis.dsn,
    client_side=True,
    retry_on_timeout=True,
    hash_key=settings_redis.HASH_KEY,
)

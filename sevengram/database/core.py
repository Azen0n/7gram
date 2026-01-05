from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr

from sevengram.config import settings
from sevengram.database.utils import build_model_representation, resolve_table_name

metadata = MetaData(
    naming_convention={
        'ix': '%(column_0_label)s_idx',
        'uq': '%(table_name)s_%(column_0_name)s_key',
        'ck': '%(table_name)s_%(constraint_name)s_check',
        'fk': '%(table_name)s_%(column_0_name)s_fkey',
        'pk': '%(table_name)s_pkey',
    },
)


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls):
        return resolve_table_name(cls.__name__)

    def __repr__(self) -> str:
        return build_model_representation(self)


engine = create_async_engine(
    url=settings.database_url,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e

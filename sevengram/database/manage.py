import asyncio

from sevengram.database.core import Base, engine


async def init_database():
    import sevengram.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(init_database())

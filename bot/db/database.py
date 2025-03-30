from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import load_db_URL

engine = create_async_engine(url=f'postgresql+asyncpg{load_db_URL()}')
session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


def async_connection(method):
    async def wrapper(*args, **kwargs):
        async with session_maker() as session:
            try:
                return await method(session, *args, **kwargs)
            except Exception as ex:
                await session.rollback()
                raise ex
            finally:
                await session.close()
    return wrapper
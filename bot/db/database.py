from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from decouple import config

database_url = f'://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST', default='localhost')}:{config('DB_PORT', default='5432')}/{config('DATABASE')}'
engine = create_async_engine(url=f'postgresql+asyncpg' + database_url)
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, exists, delete, case
import pdb
from .database import async_connection
from .models import Anket, MediaFile, Like

from typing import List, Tuple
from datetime import date


@async_connection
async def add_anket(session: AsyncSession, tg_id: int, name: str, age: int, gender: bool, interest: int,
                    city: str, description: str, status: bool) -> None:
    anket = Anket(id=tg_id, name=name, age=age, male=gender, interest=interest, city=city,
                  description=description, active=status)
    await session.merge(anket)
    await session.commit()


@async_connection
async def add_media(session: AsyncSession, tg_id: int, media: List[str], is_video: bool) -> None:
    await session.execute(delete(MediaFile).where(MediaFile.user == tg_id))
    files_to_save = [MediaFile(user=tg_id, file=file_id, video=is_video) for file_id in media]
    # await session.delete(files_to_delete)
    session.add_all(files_to_save)
    await session.commit()


@async_connection
async def change_anket_status(session: AsyncSession, tg_id: int, status: bool) -> None:
    user = await session.scalar(select(Anket).filter_by(id=tg_id))
    user.active = status
    await session.merge(user)
    await session.commit()

# @async_connection
# async def delete_user_media(session: AsyncSession, tg_id: int) -> None:
#     Files = await session.execute(select(MediaFile).where(MediaFile.user == tg_id))
#     await session.delete(Files)
#     await session.commit()

@async_connection
async def get_ankets_queue(session: AsyncSession, tg_id: int, dt: int, n: int):
    # Упорядочиваем по соответствию значению
    usr = await session.scalar(select(Anket).filter_by(id=tg_id))
    intr = (False, True,) if usr.interest == 2 else (bool(usr.interest),)
    result = await session.execute(
        select(Anket.id)
        .where(
            Anket.id != tg_id,
            Anket.age.in_(range(usr.age - dt, usr.age + dt)),
            Anket.male.in_(intr),
            Anket.active == True
        )
        .order_by(case((Anket.city == usr.city, 0), else_=1))
        .offset(n * 20)
        .limit(20)
    )
    return result.scalars().all()


@async_connection
async def get_anket(session: AsyncSession, tg_id: int) -> Anket | None:
    return await session.scalar(select(Anket).filter_by(id=tg_id))


@async_connection
async def check_anket_status(session: AsyncSession, tg_id: int) -> Anket | None:
    return await session.scalar(select(Anket.active).filter_by(id=tg_id))



@async_connection
async def get_media(session: AsyncSession, tg_id: int) -> Anket | None:
    result = await session.execute(select(MediaFile).where(MediaFile.user == tg_id))
    return list(result.scalars())


@async_connection
async def save_like(session: AsyncSession, user_id: int, anket_id: int, message: str = None) -> None:
    like = Like(sender=user_id, recipient=anket_id, message=message)
    session.add(like)
    await session.commit()


@async_connection
async def get_likes(session: AsyncSession, tg_id: int) -> List[Like]:
    result = await session.execute(select(Like).where(Like.recipient == tg_id))
    return list(result.scalars())

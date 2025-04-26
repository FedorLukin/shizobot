from sqlalchemy import BigInteger, Integer, Text, String, Boolean, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Anket(Base):
    __tablename__ = 'ankets'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    male: Mapped[bool] = mapped_column(Boolean, nullable=False)
    interest: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    city: Mapped[str] = mapped_column(String(32), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class MediaFile(Base):
    __tablename__ = 'media'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file: Mapped[str] = mapped_column(String(96), nullable=False)
    video: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Like(Base):
    __tablename__ = 'likes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sender_username: Mapped[str] = mapped_column(String(34), nullable=False)
    recipient_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)


class Admin(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
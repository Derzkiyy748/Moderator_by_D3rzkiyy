import os


from sqlalchemy import BigInteger, ForeignKey, String,  Column, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from dotenv import load_dotenv


load_dotenv(dotenv_path="bot/misc/.env")
SQLITEALHEMY_URL = os.getenv('SQLITEALHEMY_URL_BOT')



# Создание асинхронного SQLite-движка с использованием предоставленной конфигурации
engine = create_async_engine(SQLITEALHEMY_URL, echo=True)

# Создание асинхронного сессионного объекта для работы с движком
async_session = async_sessionmaker(engine)

# Определение базового класса для декларативного определения моделей данных
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Определение модели данных для пользователя
class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    chat_id: Mapped[int] = mapped_column()
    nick: Mapped[str] = mapped_column(default="")
    rank: Mapped[int] = mapped_column(default=0)


class Chat(Base):
    __tablename__ = "chat"
    chat_id: Mapped[int] = mapped_column(primary_key=True)
    chat_name: Mapped[str] = mapped_column(String(50))
    antiflood: Mapped[int] = mapped_column(default=0)
    filter_words: Mapped[str] = mapped_column(default="")


class Ban(Base):
    __tablename__ = "ban"
    ban_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    chat_id: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column()
    date: Mapped[int] = mapped_column(BigInteger)
    appealed: Mapped[str] = mapped_column(default='False')
    reason_appealed: Mapped[str] = mapped_column(default=" ")


class Mute(Base):
    __tablename__ = "mute"
    mute_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    chat_id: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column()
    date: Mapped[int] = mapped_column(BigInteger)
    appealed: Mapped[str] = mapped_column(default='False')
    reason_appealed: Mapped[str] = mapped_column(default=" ")


class Warn(Base):
    __tablename__ = "warn"
    warn_id: Mapped[int] = mapped_column(primary_key=True)
    count_warn: Mapped[int] = mapped_column()
    user_id: Mapped[int] = mapped_column()
    chat_id: Mapped[int] = mapped_column()
    reason_1: Mapped[str] = mapped_column(default=" ")
    reason_2: Mapped[str] = mapped_column(default=" ")
    reason_3: Mapped[str] = mapped_column(default=" ")


class NickName(Base):
    __tablename__ = "nickname"
    nickname_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column()
    chat_id: Mapped[int] = mapped_column()
    nickname: Mapped[str] = mapped_column()


     
async def asyn_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
    name = mapped_column(String(30))
    username: Mapped[str] = mapped_column(default=" ")
    balance: Mapped[int] = mapped_column(default=0)
    registration: Mapped[str] = mapped_column(default='False')
    ban: Mapped[str] = mapped_column(default='False')
    registration_time =  mapped_column(String)
    mode: Mapped[str] = mapped_column(default='user')
    soglashenie: Mapped[str] = mapped_column(default="False")


     
async def asyn_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
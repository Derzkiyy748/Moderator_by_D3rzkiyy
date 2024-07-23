import datetime
from sqlalchemy import BigInteger, ForeignKey, String,  Column, Integer, select
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from database.models import async_session, Chat, User, Mute, Ban

from aiogram import Bot
from aiogram.types import ChatMemberOwner



class DatabaseGroup:
    @staticmethod
    async def registered_chats(chat_id: int, chat_name: str):
        async with async_session() as session:  # Предполагаем, что async_session определен где-то в вашем коде
            res = await session.execute(select(Chat).where(Chat.chat_id == chat_id))
            chat = res.scalar_one_or_none()  # Используем scalar_one_or_none() для получения результата или None
            if chat is None:
                new_chat = Chat(chat_id=chat_id, chat_name=chat_name)
                session.add(new_chat)
                await session.commit()
                return False  # Возвращаем False, если чат был зарегистрирован
            else:
                return True  # Возвращаем True, если чат уже зарегистрирован
            

    @staticmethod
    async def add_user(user_id: int, chat_id: int, username: str, bot: Bot):
        async with async_session() as session:
            try:

                member = await bot.get_chat_member(chat_id, user_id)
                if isinstance(member, ChatMemberOwner):
                    role = '5'
                else:
                    role = '0'

                # Исправление: выберите User с правильным условием
                res = await session.execute(select(User).where(User.user_id == user_id))
                user = res.scalar_one_or_none()

                if user is None:
                    user = User(user_id=user_id, chat_id=chat_id, username=username, rank=role)
                    session.add(user)
                    await session.commit()
                    return True
                else:
                    return False
            except Exception as e:
                await session.rollback()
                raise e
            

    @staticmethod
    async def get_user_rank(user_id: int, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(User.rank).where(User.user_id == user_id, User.chat_id == chat_id))
            user_rank = res.scalar_one_or_none()
            if user_rank:
                return user_rank
            return None
        

    @staticmethod
    async def mute_user(user_id: int, chat_id: int, mute_until: int, reason: str = None):

        async with async_session() as session:
            async with session.begin():
                mute_record = Mute(
                    user_id=user_id,
                    chat_id=chat_id,
                    reason=reason,
                    date=mute_until
                )
                session.add(mute_record)
            await session.commit()


    @staticmethod
    async def ban_user(user_id: int, chat_id: int, ban_until: int, reason: str = None):

        async with async_session() as session:
            async with session.begin():
                ban_record = Ban(
                    user_id=user_id,
                    chat_id=chat_id,
                    reason=reason,
                    date=ban_until
                )
                session.add(ban_record)
            await session.commit()
    

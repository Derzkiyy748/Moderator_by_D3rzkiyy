import datetime
from sqlalchemy import BigInteger, ForeignKey, String,  Column, Integer, select, insert
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from database.models import Warn, async_session, Chat, User, Mute, Ban

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
    async def unmute_user(user_id: int, chat_id: int, reason_appealed: str):
        async with async_session() as session:
            result = await session.execute(
                select(Mute)
                .where(Mute.user_id == user_id, Mute.chat_id == chat_id, Mute.appealed == 'False')
                .order_by(Mute.date.desc())  # Сортировка по дате в порядке убывания
                .limit(1)  # Берем только одну запись
            )
            mute_record = result.scalar_one_or_none()

            if mute_record:
                mute_record.appealed = True
                mute_record.reason_appealed = reason_appealed  # Обновляем поле reason_appealed
                await session.commit()
                return True
            else:
                return False


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

    @staticmethod
    async def unban_user(user_id: int, chat_id: int, reason_appealed: str = None):

        async with async_session() as session:
            result = await session.execute(
                select(Ban)
                .where(Ban.user_id == user_id, Ban.chat_id == chat_id, Ban.appealed == 'False')
            )
            mute_record = result.scalar_one_or_none()

            if mute_record:
                mute_record.appealed = 'True'
                mute_record.reason_appealed = reason_appealed
                await session.commit()



    @staticmethod
    async def warn_user(user_id: int, chat_id: int, reason: str = None):

        """
         Я вообще не ебу, почему count_warn не обновляется до 3, а reason не записывается в reason_3,
         но это РАБОТАЕТ, пока что так оставлю)) xDD
        """

        async with async_session() as session:
            result = await session.execute(
                select(Warn)
                .where(Warn.user_id == user_id, Warn.chat_id == chat_id)
            )
            warn_record = result.scalar_one_or_none()

            if warn_record is None:
                warn_record = Warn(
                    user_id=user_id, chat_id=chat_id, 
                    reason_1=reason, reason_2=None, reason_3=None, count_warn=1
                )
                session.add(warn_record)
                warn_count = 1
            else:
                warn_count = warn_record.count_warn
                if warn_count == 1:
                    warn_record.reason_2 = reason
                    warn_record.count_warn = 2
                    warn_count = 2
                elif warn_count == 2:
                    warn_record.reason_3 = reason
                    warn_record.count_warn = 3
                    warn_count = 3
                else:
                    warn_count += 1  # Этот случай не должен происходить, но на всякий случай.

                if warn_count >= 3:
                    return "banned", warn_count

            await session.commit()
            return "warned", warn_count
        

    @staticmethod
    async def unwarn_user(user_id: int, chat_id: int) -> bool:
        async with async_session() as session:
            async with session.begin():
                # Найти последнюю запись предупреждения для пользователя
                result = await session.execute(
                    select(Warn)
                    .where(Warn.user_id == user_id, Warn.chat_id == chat_id)
                    .order_by(Warn.count_warn.desc())
                    .limit(1)
                )
                warn_record = result.scalar_one_or_none()

                if warn_record:
                    # Удаление последнего предупреждения
                    if warn_record.reason_3:
                        warn_record.reason_3 = None
                    elif warn_record.reason_2:
                        warn_record.reason_2 = None
                    elif warn_record.reason_1:
                        warn_record.reason_1 = None
                    
                    warn_record.count_warn -= 1
                    if warn_record.count_warn == 0:
                        await session.delete(warn_record)
                    await session.commit()
                    return True
                return False



    

import datetime
from typing import List
from sqlalchemy import BigInteger, ForeignKey, String,  Column, Integer, delete, select, insert, update
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from database.models import NickName, Warn, async_session, Chat, User, Mute, Ban

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
           
            # Получаем информацию о пользователе в чате
            member = await bot.get_chat_member(chat_id, user_id)
            if isinstance(member, ChatMemberOwner):
                role = '5'
            else:
                role = '0'

            # Проверяем, существует ли запись для данного user_id и chat_id
            res = await session.execute(select(User).where(User.user_id == user_id, User.chat_id == chat_id))
            user = res.scalar_one_or_none()

            if user is None:
                # Создаем новую запись для пользователя с новым chat_id
                user = User(user_id=user_id, chat_id=chat_id, username=username, rank=role)
                session.add(user)
                await session.commit()
                return True
            return False
            

    @staticmethod
    async def get_user(user_id: int, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(User).where(User.user_id == user_id, User.chat_id == chat_id))
            return res.scalar_one_or_none()
        

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
    async def unwarn_user(user_id: int, chat_id: int):
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
            
    @staticmethod
    async def get_nick(user_id: int, chat_id: int) -> str:
        async with async_session() as session: 
            result = await session.execute(
                select(User.nick).where(User.user_id == user_id, User.chat_id == chat_id))

            result_2 = await session.execute(select(User.username).where(User.user_id == user_id, User.chat_id == chat_id))
            
            nick = result.scalar_one_or_none()
            username = result_2.scalar_one_or_none()

            if nick is None:
                return username
            else:
                return nick
            
    @staticmethod
    async def set_nick(user_id: int, chat_id: int, nick: str) -> bool:
        async with async_session() as session:
            # Проверяем, существует ли ник у пользователя в таблице NickName
            result = await session.execute(
                select(NickName).where(NickName.user_id == user_id, NickName.chat_id == chat_id)
            )
            existing_nick = result.scalar_one_or_none()

            if existing_nick != None:
                # Если ник существует, удаляем старую запись в таблице NickName и сасдаем новаю
                await session.execute(
                    delete(NickName).where(NickName.user_id == user_id, NickName.chat_id == chat_id)
                )
                await session.execute(
                    insert(NickName).values(user_id=user_id, chat_id=chat_id, nickname=nick)
                )
                await session.commit()
            else:
                # Если ника нет, просто сасдаем новаю
                await session.execute(
                    insert(NickName).values(user_id=user_id, chat_id=chat_id, nickname=nick)
                )

            # Обновляем ник в таблице User | бро, это не гпт, это я ебусь с коммами
            await session.execute(
                update(User).where(User.user_id == user_id, User.chat_id == chat_id).values(nick=nick)

            )
            await session.commit()

        #await session.commit()
        #return True


    @staticmethod
    async def del_nick(user_id: int, chat_id: int) -> bool:
        async with async_session() as session:
            await session.execute(
                delete(NickName).where(NickName.user_id == user_id, NickName.chat_id == chat_id)
            )
            await session.execute(
                update(User).where(User.user_id == user_id, User.chat_id == chat_id).values(nick=None)
            )
            await session.commit()


    @staticmethod
    async def rank_up(user_id: int, chat_id: int, rank: int) -> None:
        async with async_session() as session:
            await session.execute(
                        update(User).where(User.user_id == user_id, User.chat_id == chat_id).values(rank=rank)
                    )
            await session.commit()

    """
    rank_back
    """


    @staticmethod
    async def staff(chat_id: int, rank: int) -> list:
        async with async_session() as session:
            result = await session.execute(
                select(User.user_id, User.nick, User.username).where(User.chat_id == chat_id, User.rank == rank)
            )
            staff = result.all()
            return [(user_id, nick, username) for user_id, nick, username in staff]

                
    @staticmethod
    async def zov_user(chat_id: int) -> list:
        async with async_session() as session:
            result = await session.execute(
                select(User.user_id, User.nick, User.username).where(User.chat_id == chat_id)
            )
            users = result.all()
            return [(user_id, nick, username) for user_id, nick, username in users]


    @staticmethod
    async def search_nick(user_id: str, chat_id: int) -> User:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id, User.chat_id == chat_id)
            )
            return result.scalar_one_or_none()
        

    @staticmethod
    async def get_warns(user_id: int, chat_id: int) -> Warn:
        async with async_session() as session:
            result = await session.execute(
                select(Warn).where(Warn.user_id == user_id, Warn.chat_id == chat_id)
            )
            warn = result.scalar_one_or_none()
            return warn
        
    @staticmethod
    async def get_all_warns(chat_id: int) -> list:
        async with async_session() as session:
            result = await session.execute(
                select(Warn).where(Warn.chat_id == chat_id)
            )
            warns = result.scalars().all()
            return warns
        
    @staticmethod
    async def get_muted_users(chat_id: int) -> list[Mute]:
        async with async_session() as session:
            result = await session.execute(
                select(Mute).where(Mute.chat_id == chat_id).order_by(Mute.user_id, Mute.date.desc())
            )
            muted_users = result.scalars().all()

            # Используем словарь для хранения последнего мьюта каждого пользователя
            unique_users = {}
            for mute in muted_users:
                if mute.user_id not in unique_users:
                    unique_users[mute.user_id] = mute

            return list(unique_users.values())
        

    @staticmethod
    async def get_ban_users(chat_id: int) -> list[Ban]:
        async with async_session() as session:
            result = await session.execute(
                select(Ban).where(Mute.chat_id == chat_id).order_by(Ban.user_id, Ban.date.desc())
            )
            muted_users = result.scalars().all()

            # Используем словарь для хранения последнего мьюта каждого пользователя
            unique_users = {}
            for ban in muted_users:
                if ban.user_id not in unique_users:
                    unique_users[ban.user_id] = ban

            return list(unique_users.values())
        
    @staticmethod
    async def search_ban(user_id: int, chat_id: int) -> Ban:
        async with async_session() as session:

                result = await session.execute(
                    select(Ban)
                    .where(Ban.user_id == user_id, Ban.chat_id == chat_id)
                    .order_by(Ban.ban_id.desc())  # Замените на ваше поле времени создания
                    .limit(1)  # Возвращаем только одну запись
                )
                ban = result.scalar_one_or_none()
                return ban
        
    
    @staticmethod
    async def del_all_nick(chat_id: int) -> None:
        async with async_session() as session:
            # Удаляем все записи в таблице NickName для данного чата
            await session.execute(delete(NickName).where(NickName.chat_id == chat_id))
            await session.commit()

            await session.execute(
                update(User).where(User.user_id == select(NickName.user_id).where(NickName.chat_id == chat_id)).values(nick="")
            )
            await session.commit()
            return True
        
    
    @staticmethod
    async def get_chat(chat_id: int) -> Chat:
        async with async_session() as session:
            result = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )
            return result.scalar_one_or_none()
        

    @staticmethod
    async def get_filter_words(chat_id: int) -> List[str]:
        async with async_session() as session:
            result = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )
            chat = result.scalar_one_or_none()
            if chat and hasattr(chat, 'filter_words'):
                # Проверим, является ли filter_words списком
                if isinstance(chat.filter_words, list):
                    return chat.filter_words
                # Если filter_words является строкой, разбиваем её по запятым
                elif isinstance(chat.filter_words, str):
                    return chat.filter_words.split(',')
            return []
        

    @staticmethod
    async def add_filter_word(chat_id: int, word: str) -> None:
        async with async_session() as session:
            result = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )
            chat = result.scalar_one_or_none()
            if chat and hasattr(chat, 'filter_words'):
                if isinstance(chat.filter_words, list):
                    chat.filter_words.append(word)
                elif isinstance(chat.filter_words, str):
                    chat.filter_words = f"{chat.filter_words}, {word}"
            await session.commit()


    @staticmethod
    async def remove_filter_word(chat_id: int, word: str) -> bool:
        async with async_session() as session:
            result = await session.execute(
                select(Chat).where(Chat.chat_id == chat_id)
            )
            chat = result.scalar_one_or_none()
            if chat and hasattr(chat, 'filter_words'):
                if isinstance(chat.filter_words, list):
                    # Приводим все слова к нижнему регистру для корректного сравнения
                    lowercase_words = [w.lower().strip() for w in chat.filter_words]
                    if word.lower().strip() in lowercase_words:
                        chat.filter_words.remove(word.lower().strip())
                    else:
                        return False
                elif isinstance(chat.filter_words, str):
                    words = [w.strip() for w in chat.filter_words.split(',')]
                    if word.lower().strip() in [w.lower() for w in words]:
                        words.remove(word.lower().strip())
                        chat.filter_words = ', '.join(words)
                    else:
                        return False
            await session.commit()
            return True
        

    @staticmethod
    async def get_limit_message(chat_id: int) -> int:
        async with async_session() as session:
            result = await session.execute(
                select(Chat.antiflood).where(Chat.chat_id == chat_id)
            )
            limit_message = result.scalar_one_or_none()
            if limit_message == 0:
                return 999
            else:
                return limit_message
            

    @staticmethod
    async def set_limit_message(chat_id: int, limit: int) -> None:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(Chat.chat_id == chat_id).values(antiflood=limit)
            )
            await session.commit()


    @staticmethod
    async def set_welcome_message(chat_id: int, message: str) -> None:
        async with async_session() as session:
            await session.execute(
                update(Chat).where(Chat.chat_id == chat_id).values(welcome_message=message)
            )
            await session.commit()


    @staticmethod
    async def get_all_nick(chat_id: int) -> list:
        async with async_session() as session:
            result = await session.execute(
                select(NickName).where(NickName.chat_id == chat_id)
            )
            nicknames = result.scalars().all()
            return nicknames
        

    @staticmethod
    async def get_user_rank_1(user_id: int, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(User.rank).where(User.user_id == user_id, User.chat_id == chat_id))
            user_rank = res.scalar_one_or_none()
            
            # Логирование для отладки
            print(f"get_user_rank_1: user_id={user_id}, chat_id={chat_id}, user_rank={user_rank}")
            
            return user_rank if user_rank is not None else 0  # Возвращаем 0, если ранг не найден
            
        

    
    

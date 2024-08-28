import datetime
from typing import List
from sqlalchemy import BigInteger, ForeignKey, String,  Column, Integer, delete, select, insert, update
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from database.models import NickName, Warn, async_session, Chat, User, Mute, Ban

from aiogram import Bot
from aiogram.types import ChatMemberOwner



class DatabaseGroupS:
    @staticmethod
    async def get_user_1(user_id: int, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(User).where(User.user_id == user_id, User.chat_id == chat_id))
            return res.scalar_one_or_none()
        
    @staticmethod
    async def get_user_rank(user_id: int):
        async with async_session() as session:

            # Получаем все записи с заданным user_id
            res = await session.execute(select(User.rank).where(User.user_id == user_id))
            user_ranks = res.scalars().all()
            
            # Проверяем, есть ли среди них rank == 6
            has_rank_6 = any(rank == 6 for rank in user_ranks)

            if has_rank_6:
                return has_rank_6
            
            return False
        
        
    @staticmethod
    async def get_all_chats():
        async with async_session() as session:
            result = await session.execute(select(Chat.chat_id))
            chats = result.scalars().all()
            return chats
        
    @staticmethod
    async def get_all_users():
        async with async_session() as session:
            result = await session.execute(select(User.user_id))
            users = result.scalars().all()
            return users
        
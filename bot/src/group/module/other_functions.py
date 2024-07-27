import asyncio
import re

from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.types import ChatPermissions, Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.utils.markdown import hlink

from src.group.request import DatabaseGroup
import time


db = DatabaseGroup()


class RankToUser:
    @staticmethod
    async def rank_(user_id: int, chat_id: int):
        use = await db.get_user_rank(user_id, chat_id)

        user_rank_dict = {
            '1': "модератор(а,ом)",
            '2': "администратор(а,ом)",
            '3': "старший(им) администратор(а,ом)",
            '4': "спец администратор(а,ом)",
            '5': "создатель(я,ем) беседы",
            '6': "french_dev"
            }
        
        return user_rank_dict.get(str(use), "пользователь(я)")
        



from aiogram import Bot
from contextlib import suppress
import logging
from aiogram.types import Message

from datetime import datetime, timedelta

from aiogram.utils.markdown import hlink

from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from aiogram.filters import CommandObject

from src.group.request import DatabaseGroup
from pymorphy2 import MorphAnalyzer
from src.group.module.rank import RankToUser


db = DatabaseGroup()
r = RankToUser()


class IdUser:
    @staticmethod
    async def get_id(message: Message, bot: Bot, command: CommandObject | None = None):
        
        user_id = message.reply_to_message.from_user.id

        await message.reply(f'<b>ID пользователя:</b> <i>{user_id}</i>', parse_mode='html')
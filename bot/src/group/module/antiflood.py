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
from src.group.module.other_functions import RankToUser
from src.group.module.mute import Mute
import time

r = RankToUser()
db = DatabaseGroup()


class AddMessage:
    @staticmethod
    async def add_message(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id
        parts = message.text.split(maxsplit=1)

        user_rank = await db.get_user_rank_1(user_id, chat_id)

        if len(parts) < 2:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return
        
        if not parts[1].isdigit():
            await message.reply('Неправильный формат лимита. Пожалуйста, укажите корректно')
            return

        if int(user_rank) >= 3:
            await db.set_limit_message(chat_id, parts[1])
            await message.reply(f'Лимит сообщений успешно установлен: {parts[1]}')

        else:
            await message.reply('У вас недостаточно прав для выполнения этой команды.')
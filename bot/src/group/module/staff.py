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


db = DatabaseGroup()
ran = RankToUser()



class Staff:
    @staticmethod
    async def staff(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        user = await db.get_user(user_id, chat_id)
        user_nick = await db.get_nick(user_id, chat_id)

        if user and int(user.rank) >= 1:
            staf = await db.staff(chat_id)

            if staf:
                staff_list = "\n".join([
                    f'<a href="https://t.me/{username}">{nick if nick else username}</a>' for _, nick, username in staf
                ])
                await message.reply(f"Список модераторов:\n{staff_list}", parse_mode='HTML', disable_web_page_preview=True)
            else:
                await message.reply("Нет модераторов в этом чате.")
        else:
            await message.reply("У вас нет прав для просмотра списка модераторов.")

        

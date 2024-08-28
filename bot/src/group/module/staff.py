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

        user_rank = await db.get_user_rank_1(user_id, chat_id)

        # Логирование для отладки
        print(f"staff: user_id={user_id}, chat_id={chat_id}, user_rank={user_rank}")

        if int(user_rank) >= 1:
            staf_1 = await db.staff(chat_id, 1)
            staf_2 = await db.staff(chat_id, 2)
            staf_3 = await db.staff(chat_id, 3)
            staf_4 = await db.staff(chat_id, 4)
            staf_5 = await db.staff(chat_id, 5)

            staff_list_1 = "\n".join([
                f'<a href="https://t.me/{username}">{nick if nick else username}</a>' for _, nick, username in staf_1
            ]) or "список пуст"
            staff_list_2 = "\n".join([
                f'<a href="https://t.me/{username}">{nick if nick else username}</a>' for _, nick, username in staf_2
            ]) or "список пуст"
            staff_list_3 = "\n".join([
                f'<a href="https://t.me/{username}">{nick if nick else username}</a>' for _, nick, username in staf_3
            ]) or "список пуст"
            staff_list_4 = "\n".join([
                f'<a href="https://t.me/{username}">{nick if nick else username}</a>' for _, nick, username in staf_4
            ]) or "список пуст"
            staff_list_5 = "\n".join([
                f'<a href="https://t.me/{username}">{nick if nick else username}</a>' for _, nick, username in staf_5
            ]) or "список пуст"

            message_text = f"""
<b>👮‍♂️ Список модераторов:</b>\n{staff_list_1}\n
<b>👨‍💼 Список администраторов:</b>\n{staff_list_2}\n
<b>👨‍💼 Список старших администраторов:</b>\n{staff_list_3}\n
<b>👨‍💼 Список спец. администраторов:</b>\n{staff_list_4}\n
<b>👑 Список создателей:</b>\n{staff_list_5}
            """
            await message.reply(text=message_text, parse_mode='HTML', disable_web_page_preview=True)

        else:
            await message.reply("❌ У вас нет прав для просмотра списка модераторов.")


        

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


class Zov:
    @staticmethod
    async def zov(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        parts = message.text.split(maxsplit=1)
        users = await db.zov_user(chat_id)

        reason = parts[1] if len(parts) > 1 else "без причины"

        emojis = ["🍎","🍐","🍊","🍋","🍌","🍉",
                  "🍇","🍓","🍈","🍒","🍑","🍍",
                  "🥥","🥝","🍅","🍆","🥑","🥦",
                  "🥒","🌶","🌽","🥕","🥔","🥐","🍞"]

        if users:
            mentions = [
                f'<a href="tg://user?id={user_id}">{emojis[i % len(emojis)]}</a>' for i, (user_id, _, _) in enumerate(users)
            ]
            mentions_message = ' '.join(mentions)
            await message.reply(f"Зов всех участников по причине <b>{reason}</b>:\n\n{mentions_message}", parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.reply("Нет участников в этом чате.")
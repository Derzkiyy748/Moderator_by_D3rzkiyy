import asyncio
import re

from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.types import ChatPermissions, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.utils.markdown import hlink

from src.private.request import DatabaseGroupS

from misc.config import BOT_USER

import time


db = DatabaseGroupS()


class StartPrivate:
    @staticmethod
    async def start_p(message: Message):

        keyboard = [
            [
                InlineKeyboardButton(text="добавить в чат", url=f"https://t.me/{BOT_USER}?startgroup=false")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer(
            "Привет, я бот для управления группой.\n\nДобавить в чат меня можно по кнопке ниже, <b>после добавления в чат, пропишите /start для регистрации чата в боте!</b>",
        parse_mode='html', reply_markup=reply_markup) 
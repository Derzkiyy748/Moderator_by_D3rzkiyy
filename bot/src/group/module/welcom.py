from contextlib import suppress
import logging
from aiogram import Bot
from aiogram.types import Message

from datetime import datetime, timedelta


from aiogram.exceptions import TelegramBadRequest
from src.group.request import DatabaseGroup
from src.group.module.other_functions import RankToUser



from aiogram.utils.markdown import hlink


r = RankToUser()
db = DatabaseGroup()


class WelcomeMessage:
    @staticmethod
    async def welcome(message: Message, bot: Bot):
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_rank = await db.get_user_rank_1(user_id, chat_id)

        parts = message.text.split(maxsplit=1)

        try:
           len(parts) < 2
        except:
            message.reply('Недостаточно аргументов')


        if int(user_rank) >= 3:
            await db.set_welcome_message(chat_id, parts[1])
            await message.reply(f'Приветственное сообщение успешно установлено: {parts[1]}')

        else:
            await message.reply('У вас недостаточно прав для выполнения этой команды.')


    @staticmethod
    async def welcome_text(message: Message, bot: Bot):
        text = await db.get_chat(message.chat.id)

        if not text.welcome_message:
            return

        await message.reply(text.welcome_message)

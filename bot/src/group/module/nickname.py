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
from src.group.module.mute import Mute
import time


db = DatabaseGroup()


class NickName:
    @staticmethod
    async def snick(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply("Использование: /snick <id юзера> <nickname>")
        
        try:
            user_id_to_nick = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return
        
        nickname = parts[2]

        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick_nick = await db.get_nick(user_id_to_nick, chat_id)

        user_rank = await db.get_user_rank(user_id, chat_id)
        user_to_nick_rank = await db.get_user_rank(user_id_to_nick, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_nick = await db.get_user(user_id_to_nick, chat_id)

        r = hlink(f'{user_to_nick_nick}', f'https://t.me/{user_to_nick.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_nick_rank):
                await message.reply(f'Пользователь {e} успешно изменил никнейм участника {r} на {nickname}',
                                    parse_mode='html', disable_web_page_preview=True)
                await db.set_nick(user_id_to_nick, chat_id, nickname)

            else:
                await message.reply('Вы не можете поставить никнейм данному пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


class UnNickName:
    @staticmethod
    async def rnick(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply("Использование: /rnick <id юзера> <nickname>")

        try:
            user_id_to_rnick = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return

        user_nick = await db.get_nick(user_id, chat_id)
        user_to_rnick_nick = await db.get_nick(user_id_to_rnick, chat_id)

        user_rank = await db.get_user_rank(user_id, chat_id)
        user_to_rnick_rank = await db.get_user_rank(user_id_to_rnick, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_rnick = await db.get_user(user_id_to_rnick, chat_id)

        r = hlink(f'{user_to_rnick_nick}', f'https://t.me/{user_to_rnick.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_rnick_rank):
                await message.reply(f'Пользователь {e} успешно сбросил никнейм участника {r}',
                                    parse_mode='html')
                await db.del_nick(user_id_to_rnick, chat_id)

            else:
                await message.reply('Вы не можете сбросить никнейм данному пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')
        
                



        



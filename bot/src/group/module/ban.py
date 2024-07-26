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


class Ban:
    @staticmethod
    async def parse_time(time_string: str | None) -> datetime | None:
        if not time_string:
            return None
        
        current_date = datetime.now()

        match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
        
        if match_:
            value, unit = int(match_.group(1)), match_.group(2)

            match unit:
                case "s": time_delta = timedelta(seconds=value)
                case "m": time_delta = timedelta(minutes=value)
                case "h": time_delta = timedelta(hours=value) 
                case "d": time_delta = timedelta(days=value)
                case _: return None  # Если единица измерения не распознана, возвращаем None
        else:
            return None
        
        new_datetime = current_date + time_delta
        return new_datetime

    @staticmethod
    async def ban(message: Message, bot: Bot, command: CommandObject | None = None):
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()
        
        # Проверка количества аргументов
        if len(parts) < 4:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        # Проверка и получение времени
        try:
            until_date = await Ban.parse_time(parts[2])  # Предполагаем, что время передается в секундах
        except ValueError:
            await message.reply('Неправильный формат времени. Пожалуйста, укажите вид времени(s, m, h, d).\n\nПример: /ban 77777777 40m спам')
            return

        reason = parts[3]

        try:
            user_id_to_ban = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return
        
        user_nick = await db.get_nick(user_id, chats_id)
        user_to_ban_nick = await db.get_nick(user_id_to_ban, chats_id)

        user_rank = await db.get_user_rank(user_id, chats_id)
        user_to_ban_rank = await db.get_user_rank(user_id_to_ban, chats_id)

        user = await db.get_user(user_id, chats_id)
        user_to_ban = await db.get_user(user_id_to_ban, chats_id)

        r = hlink(f'{user_to_ban_nick}', f'https://t.me/{user_to_ban.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 2:
            if int(user_rank) >= int(user_to_ban_rank):
                with suppress(TelegramBadRequest):
                    await bot.ban_chat_member(chats_id,
                                              user_id_to_ban,
                                              until_date=until_date)
                    
                    await db.ban_user(user_id_to_ban, chats_id, until_date, reason)
                    await message.reply(f'участник {r} был забанен пользователем {e} по причине: {reason}\nВремя разблокировки: {until_date}.', parse_mode='html')
            else:
                await message.reply('Вы не можете забанить данного пользователя.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


class UnBan:
    @staticmethod
    async def unban(message: Message, bot: Bot, command: CommandObject | None = None):

        '''
        ERROR!! участник <a href="https://t.me/D3rzkiyy">D3rzkiyy</a> был разбанен пользователем <a href="https://t.me/khavr_global">khavr_global</a> по причине: sorry
        '''
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split(maxsplit=2)
        
        # Проверка количества аргументов
        if len(parts) < 3:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_unban = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return
        
        reason = parts[2]

        user_nick = await db.get_nick(user_id, chats_id)
        user_to_unban_nick = await db.get_nick(user_id_to_unban, chats_id)

        user_rank = await db.get_user_rank(user_id, chats_id)
        user_to_unban_rank = await db.get_user_rank(user_id_to_unban, chats_id)

        user = await db.get_user(user_id, chats_id)
        user_to_unban = await db.get_user(user_id_to_unban, chats_id)

        r = hlink(f'{user_to_unban_nick}', f'https://t.me/{user_to_unban.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 2:
            if int(user_rank) >= int(user_to_unban_rank):
                with suppress(TelegramBadRequest):
                    await db.unban_user(user_id_to_unban, chats_id, reason)
                    await bot.unban_chat_member(chats_id, user_id_to_unban)
                    await message.reply(f'участник {r} был разбанен пользователем {e} по причине: {reason}',
                                        parse_mode='html', disable_web_page_preview=True)
            else:
                await message.reply('Вы не можете разбанить данного пользователя.')
        else:
            await message.reply('Вы не можете использовать эту команду.')



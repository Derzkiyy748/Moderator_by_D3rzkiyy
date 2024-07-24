import asyncio
import re

from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.types import ChatPermissions, Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject

from src.group.request import DatabaseGroup
from src.group.module.mute import Mute
import time


db = DatabaseGroup()


class Warn:
    @staticmethod
    async def warn(message: Message, bot: Bot, command: CommandObject | None = None):
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()
        
        # Проверка количества аргументов
        if len(parts) < 3:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        reason = parts[2]

        try:
            user_id_to_warn = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return

        user_rank = await db.get_user_rank(user_id, chats_id)
        user_to_warn_rank = await db.get_user_rank(user_id_to_warn, chats_id)

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_warn_rank):
                result, warn_count = await db.warn_user(user_id_to_warn, chats_id, reason)
                if result == "warned":
                    await message.reply(f'Пользователь {user_id_to_warn} получил предупреждение по причине: {reason}. У пользователя {warn_count} предупреждение(й).')
                elif result == "banned":
                    current_date = datetime.now()
                    time_delta = timedelta(days=15) 
                    until_date = current_date + time_delta

                    await db.ban_user(user_id_to_warn,
                                      chats_id,
                                      until_date,
                                      reason="Максимальное количество нарушений (3/3)")
                    
                    with suppress(TelegramBadRequest):

                        await bot.ban_chat_member(chats_id,
                                                user_id_to_warn,
                                                until_date=until_date)
                        await message.reply(f'Пользователь {user_id_to_warn} был забанен на 15 дней за превышение количества предупреждений (3/3).')
            else:
                await message.reply('Вы не можете выдать предупреждение этому пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')

class UnWarn:
    @staticmethod
    async def unwarn(message: Message, bot: Bot, command: CommandObject | None = None):
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        # Проверка количества аргументов
        if len(parts) < 2:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_unwarn = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return

        user_rank = await db.get_user_rank(user_id, chats_id)
        user_to_unwarn_rank = await db.get_user_rank(user_id_to_unwarn, chats_id)
        reason = parts[2]

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_unwarn_rank):
                result = await db.unwarn_user(user_id_to_unwarn, chats_id)
                if result:
                    await message.reply(f'Предупреждение снято с пользователя {user_id_to_unwarn} по причине: {reason}.')
                else:
                    await message.reply('Не удалось найти предупреждения для данного пользователя или все предупреждения уже сняты.')
            else:
                await message.reply('Вы не можете снять предупреждение с данного пользователя.')
        else:
            await message.reply('Вы не можете использовать эту команду.')



                

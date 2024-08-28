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


class Warn:
    @staticmethod
    async def warn(message: Message, bot: Bot, command: CommandObject | None = None):
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split(maxsplit=2)
        
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

        user_nick = await db.get_nick(user_id, chats_id)
        user_to_warn_nick = await db.get_nick(user_id_to_warn, chats_id)

        user_rank = await db.get_user_rank_1(user_id, chats_id)
        user_to_warn_rank = await db.get_user_rank_1(user_id_to_warn, chats_id)

        user = await db.get_user(user_id, chats_id)
        user_to_warn = await db.get_user(user_id_to_warn, chats_id)

        r = hlink(f'{user_to_warn_nick}', f'https://t.me/{user_to_warn.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_warn_rank):
                result, warn_count = await db.warn_user(user_id_to_warn, chats_id, reason)
                if result == "warned":
                    await message.reply(f'Участник {r} получил предупреждение от пользователя {e}. У участника {warn_count} предупреждение(й).',
                                        parse_mode='html', disable_web_page_preview=True)
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
                        await message.reply(f'участник {user_id_to_warn} был забанен на 15 дней за превышение количества предупреждений (3/3).')
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

        user_nick = await db.get_nick(user_id, chats_id)
        user_to_unwarn_nick = await db.get_nick(user_id_to_unwarn, chats_id)

        user_rank = await db.get_user_rank_1(user_id, chats_id)
        user_to_unwarn_rank = await db.get_user_rank_1(user_id_to_unwarn, chats_id)

        user = await db.get_user(user_id, chats_id)
        user_to_unwarn = await db.get_user(user_id_to_unwarn, chats_id)

        r = hlink(f'{user_to_unwarn_nick}', f'https://t.me/{user_to_unwarn.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        reason = parts[2]

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_unwarn_rank):
                result = await db.unwarn_user(user_id_to_unwarn, chats_id)
                if result:
                    await message.reply(f'Пользователь {e} снял предупреждение с участника {r} по причине: {reason}',
                                        parse_mode='html')
                else:
                    await message.reply('Не удалось найти предупреждения для данного пользователя или все предупреждения уже сняты.')
            else:
                await message.reply('Вы не можете снять предупреждение с данного пользователя.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


class SearchWarn:
    @staticmethod
    async def search_warn(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        if len(parts) < 2:
            return await message.reply("Использование: /gwarn <id пользователя>")

        user_id_to_search = int(parts[1])

        user_rank = await db.get_user_rank_1(user_id, chat_id)
        user = await db.get_user(user_id, chat_id)

        if int(user_rank) >= 1:
            war = await db.get_warns(user_id_to_search, chat_id)
            user_to_search = await db.get_user(user_id_to_search, chat_id)

            if user_to_search:
                user_link = hlink(f'{user_to_search.nick}' if user_to_search.nick else f'{user_to_search.username}', f'https://t.me/{user_to_search.username}')

                if war:
                    reasons = [war.reason_1, war.reason_2, war.reason_3]
                    reasons = [reason for reason in reasons if reason.strip()]  # Удаление пустых причин
                    warn_list = "\n".join(reasons)
                    await message.reply(f'Предупреждения {user_link}:\n\nКоличество предупреждений: {war.count_warn}\nПричины:\n{warn_list}', parse_mode='HTML',
                                        disable_web_page_preview=True)
                else:
                    await message.reply(f'У {user_link} нет предупреждений.', parse_mode='HTML',
                                        disable_web_page_preview=True)
            else:
                await message.reply('Пользователь с таким ID не найден.')
        else:
            await message.reply('У вас нет прав для использования этой команды.')


class WarnList:
    @staticmethod
    async def list_warns(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        user_rank = await db.get_user_rank_1(user_id, chat_id)
        user = await db.get_user(user_id, chat_id)

        if int(user_rank) >= 1:
            warns = await db.get_all_warns(chat_id)
            if warns:
                warn_details = []
                for warn in warns:
                    if warn:  # Проверка на None
                        user_to_search = await db.get_user(warn.user_id, chat_id)
                        if user_to_search:  # Проверка на None
                            user_link = hlink(f'{user_to_search.nick}' if user_to_search.nick else f'{user_to_search.username}', f'https://t.me/{user_to_search.username}')
                            reasons = [warn.reason_1, warn.reason_2, warn.reason_3]
                            reasons = [reason for reason in reasons if reason.strip()]  # Удаление пустых причин
                            warn_list = "\n".join(reasons)
                            warn_details.append(f'{user_link} - Количество предупреждений: {warn.count_warn}\nПричины:\n{warn_list}')
                
                if warn_details:
                    warn_message = "\n\n".join(warn_details)
                    await message.reply(f'Список предупреждений пользователей:\n\n{warn_message}', parse_mode='HTML',
                                        disable_web_page_preview=True)
                else:
                    await message.reply('В этом чате нет предупреждений.')
            else:
                await message.reply('В этом чате нет предупреждений.')
        else:
            await message.reply('У вас нет прав для использования этой команды.')




                

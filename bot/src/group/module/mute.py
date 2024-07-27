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
import time

r = RankToUser()
db = DatabaseGroup()


class Mute:
    @staticmethod
    async def parse_time(time_string: str | None) -> datetime | None:
        if not time_string:
            return None
        
        current_date = datetime.now()

        # Изменен регулярный шаблон для парсинга временной строки
        match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
        
        if match_:
            value, unit = int(match_.group(1)), match_.group(2)

            # Использование match синтаксиса для обработки единицы измерения времени
            match unit:
                case "s": time_delta = timedelta(seconds=value)
                case "m": time_delta = timedelta(minutes=value)
                case "h": time_delta = timedelta(hours=value) 
                case "d": time_delta = timedelta(days=value)
                case _: return None  # Если единица измерения не распознана, возвращаем None
        else:
            return None
        
        new_datetime = current_date + time_delta
        new_datetime = str(new_datetime).split('.')[0]
        return new_datetime
            


    async def mute(message: Message, bot: Bot, command: CommandObject | None = None):
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split(maxsplit=3)
        
        # Проверка количества аргументов
        if len(parts) < 4:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        # Проверка и получение времени
        try:
            until_date = await Mute.parse_time(parts[2])  # Предполагаем, что время передается в секундах
        except ValueError:
            await message.reply('Неправильный формат времени. Пожалуйста, укажите вид времени(s, m, h, d).\n\nПример: /mute 43553453 40m спам')
            return

        reason = parts[3]

        try:
            user_id_to_mute = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return

        user_to_mute_nick = await db.get_nick(user_id_to_mute, chats_id)
        user_nick = await db.get_nick(user_id, chats_id)

        user_rank = await db.get_user_rank(user_id, chats_id)
        user_to_mute_rank = await db.get_user_rank(user_id_to_mute, chats_id)
    

        user_to_mute = await db.get_user(user_id_to_mute, chats_id)
        user = await db.get_user(user_id, chats_id)

        r = hlink(f'{user_to_mute_nick}', f'https://t.me/{user_to_mute.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_mute_rank):
                with suppress(TelegramBadRequest):

                    p = await r.rank_(user_id, chats_id)
                    p_1 = await r.rank_(user_id_to_mute, chats_id)

                    # Используем правильную переменную `until_date`
                    await bot.restrict_chat_member(
                        chats_id,
                        user_id_to_mute,
                        until_date=until_date,
                        permissions=ChatPermissions(can_send_messages=False)
                    )
                    await message.reply(f'{p_1} {r} был замучен {p} {e} по причине: {reason}\nВремя разблокировки: {until_date}.',
                                        parse_mode='html', disable_web_page_preview=True)

                    await db.mute_user(user_id_to_mute, chats_id, until_date, reason)
            else:
                await message.reply('Вы не можете замьютить данного пользователя.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


class UnMute:
    @staticmethod
    async def unmute(message: Message, bot: Bot, command: CommandObject | None = None):
        chats_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()
        
        # Проверка количества аргументов
        if len(parts) < 3:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_unmute = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return
        
        user_nick = await db.get_nick(user_id, chats_id)
        user_to_unmute_nick = await db.get_nick(user_id_to_unmute, chats_id)

        user_rank = await db.get_user_rank(user_id, chats_id)
        user_to_unmute_rank = await db.get_user_rank(user_id_to_unmute, chats_id)
        reason_appealed = ' '.join(parts[2:])  # Объединяем все оставшиеся части в строку

        user_to_unmute = await db.get_user(user_id_to_unmute, chats_id)
        user = await db.get_user(user_id, chats_id)

        re = hlink(f'{user_to_unmute_nick}', f'https://t.me/{user_to_unmute.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user_rank) >= 1:
            if int(user_rank) >= int(user_to_unmute_rank):
                success = await db.unmute_user(user_id_to_unmute, chats_id, reason_appealed)
                if success:
                    with suppress(TelegramBadRequest):
                        p = await r.rank_(user_id, chats_id)
                        p_1 = await r.rank_(user_id_to_unmute, chats_id)
                        await bot.restrict_chat_member(
                            chats_id, 
                            user_id_to_unmute, 
                            permissions=ChatPermissions(can_send_messages=True)
                        )
                        await message.reply(
                        f'{p_1} {r} был размучен {p} {e} по причине: {reason_appealed}.',
                        parse_mode='html', disable_web_page_preview=True
                    )

                else:
                    await message.reply('Не удалось найти запись о мьюте для данного пользователя или он уже размучен.')
            else:
                await message.reply('Вы не можете размьютить данного пользователя.')
        else:
            await message.reply('Вы не можете использовать эту команду.')



class MuteList:
    @staticmethod
    async def mute_list(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        user_rank = await db.get_user_rank(user_id, chat_id)

        if int(user_rank) >= 1:
            muted_users = await db.get_muted_users(chat_id)

            if not muted_users:
                await message.reply('Список замученных пользователей пуст.')
                return

            mute_list_message = 'Список замученных пользователей:\n\n'

            for user in muted_users:
                user_nick = await db.get_nick(user.user_id, chat_id)
                user_info = await db.get_user(user.user_id, chat_id)
                user_link = hlink(f'{user_nick}' if user_nick else f'{user_info.username}', f'https://t.me/{user_info.username}')
                
                if user.appealed == 'False':
                    mute_list_message += f'{user_link} - До: {user.date}\n'

            await message.reply(mute_list_message, parse_mode='HTML', disable_web_page_preview=True)
        else:
            await message.reply('У вас нет прав для использования этой команды.')




        

        



            





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


class RankForward:
    @staticmethod
    async def rank_gmoder(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        # Проверка количества аргументов
        if len(parts) < 1:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_rank = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return


        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick = await db.get_nick(user_id_to_rank, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_rank = await db.get_user(user_id_to_rank, chat_id)

        r = hlink(f'{user_to_nick}', f'https://t.me/{user_to_rank.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user.rank) >= 2:
            if int(user_to_rank.rank) < 1:
                rank_1 = await ran.rank_(user_id_to_rank, chat_id)
                await db.rank_up(user_id_to_rank, chat_id, 1)
                rank = await ran.rank_(user_id, chat_id)
                rank_3 = await ran.rank_(user_id_to_rank, chat_id)
                await message.reply(f'{rank} {e} повысил {rank_1} {r} до {rank_3}',
                                    parse_mode='html', disable_web_page_preview=True)
            
            else:
                await message.reply('Вы не можете выдать ранк этому пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


    @staticmethod
    async def rank_gadmin(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        # Проверка количества аргументов
        if len(parts) < 1:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_rank = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return


        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick = await db.get_nick(user_id_to_rank, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_rank = await db.get_user(user_id_to_rank, chat_id)

        r = hlink(f'{user_to_nick}', f'https://t.me/{user_to_rank.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user.rank) >= 3:
            if int(user_to_rank.rank) < 2:
                rank_1 = await ran.rank_(user_id_to_rank, chat_id)
                await db.rank_up(user_id_to_rank, chat_id, 2)
                rank = await ran.rank_(user_id, chat_id)
                rank_3 = await ran.rank_(user_id_to_rank, chat_id)
                await message.reply(f'{rank} {e} повысил {rank_1} {r} до {rank_3}',
                                    parse_mode='html', disable_web_page_preview=True)
            
            else:
                await message.reply('Вы не можете выдать ранк этому пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')



    @staticmethod
    async def rank_gsenadmin(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        # Проверка количества аргументов
        if len(parts) < 1:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_rank = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return


        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick = await db.get_nick(user_id_to_rank, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_rank = await db.get_user(user_id_to_rank, chat_id)

        r = hlink(f'{user_to_nick}', f'https://t.me/{user_to_rank.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user.rank) >= 4:
            if int(user_to_rank.rank) < 3:
                rank_1 = await ran.rank_(user_id_to_rank, chat_id)
                await db.rank_up(user_id_to_rank, chat_id, 3)
                rank = await ran.rank_(user_id, chat_id)
                rank_3 = await ran.rank_(user_id_to_rank, chat_id)
                await message.reply(f'{rank} {e} повысил {rank_1} {r} до {rank_3}',
                                    parse_mode='html', disable_web_page_preview=True)
            
            else:
                await message.reply('Вы не можете выдать ранк этому пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


    @staticmethod
    async def rank_gspec(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        # Проверка количества аргументов
        if len(parts) < 1:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_rank = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return


        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick = await db.get_nick(user_id_to_rank, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_rank = await db.get_user(user_id_to_rank, chat_id)

        r = hlink(f'{user_to_nick}', f'https://t.me/{user_to_rank.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user.rank) >= 5:
            if int(user_to_rank.rank) < 4:
                rank_1 = await ran.rank_(user_id_to_rank, chat_id)
                await db.rank_up(user_id_to_rank, chat_id, 4)
                rank = await ran.rank_(user_id, chat_id)
                rank_3 = await ran.rank_(user_id_to_rank, chat_id)
                await message.reply(f'{rank} {e} повысил {rank_1} {r} до {rank_3}',
                                    parse_mode='html', disable_web_page_preview=True)
            
            else:
                await message.reply('Вы не можете выдать ранк этому пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')


    @staticmethod
    async def editowner(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        # Проверка количества аргументов
        if len(parts) < 1:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_rank = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return


        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick = await db.get_nick(user_id_to_rank, chat_id)

        user = await db.get_user(user_id, chat_id)
        user_to_rank = await db.get_user(user_id_to_rank, chat_id)

        r = hlink(f'{user_to_nick}', f'https://t.me/{user_to_rank.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user.rank) >= 5:
            if int(user_to_rank.rank) < 5:
                rank_1 = await ran.rank_(user_id_to_rank, chat_id)
                await db.rank_up(user_id_to_rank, chat_id, 5)
                rank = await ran.rank_(user_id, chat_id)
                rank_3 = await ran.rank_(user_id_to_rank, chat_id)
                await message.reply(f'{rank} {e} передал права владельца группы данному {rank_1} {r}',
                                    parse_mode='html', disable_web_page_preview=True)

            else:
                await message.reply('Вы не можете выдать ранк этому пользователю.')
        else:
            await message.reply('Вы не можете использовать эту команду.')



class RankBack:
    @staticmethod
    async def rank_back(message: Message, bot: Bot, command: CommandObject | None = None):
        chat_id = message.chat.id
        user_id = message.from_user.id
        parts = message.text.split()

        if len(parts) < 2:
            await message.reply('Недостаточно аргументов для выполнения команды.')
            return

        try:
            user_id_to_rank = int(parts[1])
        except ValueError:
            await message.reply('Неправильный формат user_id. Пожалуйста, укажите корректный user_id.')
            return

        user = await db.get_user(user_id, chat_id)
        user_to_rank = await db.get_user(user_id_to_rank, chat_id)

        user_nick = await db.get_nick(user_id, chat_id)
        user_to_nick = await db.get_nick(user_id_to_rank, chat_id)

        r = hlink(f'{user_to_nick}', f'https://t.me/{user_to_rank.username}')
        e = hlink(f'{user_nick}', f'https://t.me/{user.username}')

        if int(user.rank) >= 2 and int(user.rank) > int(user_to_rank.rank):
            rank = await ran.rank_(user_id, chat_id)
            rank_3 = await ran.rank_(user_id_to_rank, chat_id)
            await db.rank_up(user_id_to_rank, chat_id, 0)
            rank_1 = await ran.rank_(user_id_to_rank, chat_id)
            await message.reply(
                f'{rank} {e} снял {rank_1} {r} с поста {rank_3}',
                parse_mode='html', disable_web_page_preview=True
            )
        else:
            await message.reply('Вы не можете снять ранк этому пользователю.')

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

from src.group.request import DatabaseGroup
from src.group.module.other_functions import RankToUser
from src.group.module.mute import Mute
import time

r = RankToUser()
db = DatabaseGroup()


class HelpCommand:
    commands_by_rank = {
        1: [
            ("Команды для модераторов:", ""),
            ("/mute [Пользователь] [Срок в минутах] [Причина]", "Блокировка чата для пользователя на определённое время."),
            ("/unmute [Пользователь] [Причина]", "Разблокировка чата для пользователя."),
            ("/warn [Пользователь] [Причина]", "Выдача предупреждения пользователю."),
            ("/unwarn [Пользователь] [Причина]", "Снятие предупреждения с пользователя."),
            ("/snick [Пользователь] [Никнейм]", "Установка никнейма для пользователя."),
            ("/rnick [Пользователь]", "Удаление никнейма у пользователя."),
            ("/staff", "Просмотр списка модераторов."),
            ("/zov [Причина]", "Созыв всех модераторов."),
            ("/nlist", "Просмотр списка никнеймов."),
            ("/gnick [Пользователь]", "Просмотр никнейма пользователя."),
            ("/gwarn [Пользователь]", "Просмотр предупреждений пользователя."),
            ("/wlist", "Просмотр списка всех предупреждений."),
            ("/mlist", "Просмотр списка блокировок чата."),
            ("/clear [Количество сообщений]", "Удаление определённого количества сообщений."),
            ("/getban [Пользователь]", "Проверка статуса блокировки пользователя.")
        ],
        2: [
            ("/ban [Пользователь] [Срок в днях] [Причина]", "Блокировка пользователя на определённое количество дней."),
            ("/unban [Пользователь] [Причина]", "Разблокировка пользователя."),
            ("/gmoder [Пользователь]", "Выдача прав модератора (1 ранг)."),
            ("/blist", "Просмотр списка блокировок.")
        ],
        3: [
            ("/gadmin [Пользователь]", "Выдача прав администратора (2 ранг)."),
            ("/rrole [Пользователь] [Причина]", "Понижение ранга пользователя."),
            ("/rnickall", "Удаление никнеймов у всех пользователей."),
            ("/filter [Add/Remove] [Слово]", "Добавление или удаление слова из фильтра."),
            ("/antiflood [Кол-во сообщений в минуту]", "Настройка защиты от спама."),
            ("/welcometext [Текст]", "Настройка текста приветствия.")
        ],
        4: [
            ("/gsenadmin [Пользователь]", "Выдача прав старшего администратора (3 ранг).")
        ],
        5: [
            ("/gspec [Пользователь]", "Выдача прав спец. администратора (4 ранг)."),
            ("/editowner", "Передача прав владельца беседы.")
        ],
        6: [
            ("/news [Текст]", "Отправка сообщения во все беседы.")
        ]
    }

    @staticmethod
    async def help_menu(message: Message):
        buttons = [
            [InlineKeyboardButton(text="Для модератора", callback_data='help_1')],
            [InlineKeyboardButton(text="Для администратора", callback_data='help_2')],
            [InlineKeyboardButton(text="Для старшего администратора", callback_data='help_3')],
            [InlineKeyboardButton(text="Для спец. администратора", callback_data='help_4')],
            [InlineKeyboardButton(text="Для создателя беседы", callback_data='help_5')],
            [InlineKeyboardButton(text="Для владельца", callback_data='help_6')]
        ]
        
        user_rank = await db.get_user_rank_1(message.from_user.id, message.chat.id)

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.reply("Выберите категорию команд:", reply_markup=keyboard)

    @staticmethod
    async def help_detail(call: CallbackQuery, bot: Bot):
        callback_data = call.data
        if callback_data == 'help_back':
            await HelpCommand.help_back(call)
            return

        try:
            rank_requested = int(callback_data.split('_')[1])
        except ValueError:
            await call.answer("Неверный запрос.", show_alert=True)
            return

        chat_id = call.message.chat.id
        user_id = call.from_user.id
        user_rank = await db.get_user_rank_1(user_id, chat_id)

        # Проверка, если ранг пользователя меньше запрашиваемого ранга
        if int(user_rank) < int(rank_requested):
            await call.answer("У вас недостаточно прав для просмотра этой категории.", show_alert=True)
            return

        response = []

        for rank in range(1, rank_requested + 1):
            if rank in HelpCommand.commands_by_rank:
                for command, description in HelpCommand.commands_by_rank[rank]:
                    response.append(f"<i>{command}</i>\n<b>Описание</b>: {description}\n")

        if response:
            keyboard = [
                [(InlineKeyboardButton(text="Назад", callback_data='help_back'))]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await call.message.edit_text('\n'.join(response), parse_mode='html', reply_markup=keyboard)
        else:
            await call.answer("Нет команд для этого ранга.", show_alert=True)

    @staticmethod
    async def help_back(call: CallbackQuery):
        buttons = [
            [InlineKeyboardButton(text="Для модератора", callback_data='help_1')],
            [InlineKeyboardButton(text="Для администратора", callback_data='help_2')],
            [InlineKeyboardButton(text="Для старшего администратора", callback_data='help_3')],
            [InlineKeyboardButton(text="Для спец. администратора", callback_data='help_4')],
            [InlineKeyboardButton(text="Для создателя беседы", callback_data='help_5')],
            [InlineKeyboardButton(text="Для владельца", callback_data='help_6')]
        ]

        user_rank = await db.get_user_rank_1(call.from_user.id, call.message.chat.id)

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await call.message.edit_text("Выберите категорию команд:", reply_markup=keyboard)

    
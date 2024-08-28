import asyncio
import re

from contextlib import suppress
from datetime import datetime, timedelta

from aiogram import Bot, types
from aiogram.types import (ChatPermissions, Message, InlineKeyboardButton, InlineKeyboardMarkup,
                          CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject
from aiogram.utils.markdown import hlink

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class AdminStates(StatesGroup):
    waiting_for_group_mailing = State()
    waiting_for_private_mailing = State()


from src.private.request import DatabaseGroupS

db = DatabaseGroupS()


class Admin:
    @staticmethod
    async def admin(message: Message, bot: Bot):
    
        r = await db.get_user_rank(message.chat.id)
        
        if r:
            keyboard = [
                [
                    InlineKeyboardButton(text="Рассылка по чатам", callback_data="mailing_group"),
                    InlineKeyboardButton(text="Рассылка в лс", callback_data="mailing_private"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            await message.answer(f"Добро пожаловать в админ панель, {message.from_user.first_name} !\n\nВот кнопочки для тебя:" , reply_markup=reply_markup,
                                 parse_mode='html')
        return

    @staticmethod
    async def handle_callback(query: CallbackQuery, bot: Bot, state: FSMContext):

        key = [
                [
                    KeyboardButton(text="Отмена")
                ]
            ]
        reply = ReplyKeyboardMarkup(keyboard=key, resize_keyboard=True)

        if query.data == "mailing_group":
            await query.message.answer("Введите сообщение для рассылки по чатам:", reply_markup=reply)
            await state.set_state(AdminStates.waiting_for_group_mailing)
        elif query.data == "mailing_private":
            await query.message.answer("Введите сообщение для рассылки в лс:", reply_markup=reply)
            await state.set_state(AdminStates.waiting_for_private_mailing)

    @staticmethod
    async def send_group_mailing(message: Message, bot: Bot, state: FSMContext):
        await state.clear()
        chats = await db.get_all_chats()
        successful, failed = 0, 0
        for chat_id in chats:
            try:
                await bot.send_message(chat_id, message.text)
                successful += 1
            except Exception as e:
                print(f"Не удалось отправить сообщение в чат {chat_id}: {e}")
                failed += 1
        await message.answer(f"Рассылка по чатам завершена.\n\n<b>Успешных сообщений:</b> {successful}.\n<b>Неудачных сообщений:</b> {failed}.",
                            reply_markup=ReplyKeyboardRemove(), parse_mode='html')

    @staticmethod
    async def send_private_mailing(message: Message, bot: Bot, state: FSMContext):
        await state.clear()
        users = await db.get_all_users()
        successful, failed = 0, 0
        for user_id in users:
            try:
                await bot.send_message(user_id, message.text)
                successful += 1
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
                failed += 1
        await message.answer(f"Рассылка в лс завершена.\n\n<b>Успешных сообщений:</b> {successful}.\n<b>Неудачных сообщений:</b> {failed}.",
                            reply_markup=ReplyKeyboardRemove(), parse_mode='html')

    @staticmethod
    async def cancel_mailing(message: Message, bot: Bot, state: FSMContext):
        await state.clear()
        await message.answer("Рассылка отменена.", reply_markup=ReplyKeyboardRemove())
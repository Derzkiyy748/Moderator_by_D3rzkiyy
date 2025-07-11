from aiogram import Bot
from contextlib import suppress
import logging
from aiogram.types import Message

from datetime import datetime, timedelta

from aiogram.utils.markdown import hlink

from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from aiogram.filters import CommandObject

from src.group.request import DatabaseGroup
from pymorphy2 import MorphAnalyzer
from src.group.module.rank import RankToUser


db = DatabaseGroup()
r = RankToUser()


class StartBot:

    def __init__(self):
        self.chat_data = {}

    @staticmethod
    async def start(message: Message, bot: Bot, command: CommandObject | None = None):
        if await db.registered_chats(message.chat.id, message.chat.title):
            await bot.send_message(message.chat.id, "Привет, я бот для управления группой!\nДанная группа уже зарегистрирована\n\n<b>Разработано</b>: @D3rzkiyy", parse_mode='html')
        else:
            await bot.send_message(message.chat.id, "Привет, я бот для управления группой!\nДанная группа успешно зарегистрирована\n\n<b>Разработано</b>: @D3rzkiyy", parse_mode='html')

        
    @staticmethod
    async def add_usere(message: Message, bot: Bot, command: CommandObject | None = None):
        await db.add_user(message.from_user.id, message.chat.id, message.from_user.username, bot)

        chat_id = message.chat.id
        user_id = message.from_user.id  # Получение user_id пользователя

        morph = MorphAnalyzer(lang='ru')

        # Получение ника пользователя для упоминания в сообщении
        user_to_word_nick = await db.get_nick(user_id, chat_id)
        user_to_word = await db.get_user(user_id, chat_id)
        user_mention = f'<a href="https://t.me/{user_to_word.username}">{user_to_word_nick}</a>'

        trigers = await db.get_filter_words(chat_id)
        if not trigers:
            return  # Если нет триггеров в базе данных, завершить выполнение функции

        trigers = set(trigers)  # Преобразуем список триггеров в множество для оптимизации поиска

        for word in message.text.lower().strip().split():
            parse_word = morph.parse(word)[0]
            normal_form = parse_word.normal_form

            if normal_form in trigers:
                # Получение ранга пользователя
                rank = await r.rank_(user_id, chat_id)

                # Отправка предупреждения пользователю
                reason = "Использование запрещенных слов"
                result, warn_count = await db.warn_user(user_id, chat_id, reason)

                if result == "warned":
                    # Отправка сообщения о предупреждении
                    await message.reply(f'Запрещенное слово обнаружено: {normal_form}\n\n{user_mention} получил предупреждение.\nУ {rank} {warn_count} предупреждение(й).',
                                        parse_mode='html', disable_web_page_preview=True)
                elif result == "banned":
                    # Если достигнуто максимальное количество предупреждений, бан пользователя
                    current_date = datetime.now()
                    time_delta = timedelta(days=7)
                    until_date = (current_date + time_delta).strftime("%Y-%m-%d %H:%M:%S")

                    await db.ban_user(user_id, chat_id, until_date, reason="Максимальное количество нарушений (3/3)")

                    # Попытка забанить пользователя в чате Telegram
                    with suppress(TelegramBadRequest):
                        await bot.ban_chat_member(chat_id, user_id, until_date=until_date)
                        await message.reply(f'{user_mention} был забанен на 7 дней за превышение количества предупреждений (3/3).')

                # Прерываем цикл, если найдено запрещенное слово
                break

    






        
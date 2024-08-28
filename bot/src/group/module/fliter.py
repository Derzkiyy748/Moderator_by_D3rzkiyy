
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


class FilterWords:
    @staticmethod
    async def filter(message: Message, bot: Bot):
        chat_id = message.chat.id
        text = message.text.split(maxsplit=2)
        user_id = message.from_user.id

        user_to_word_nick = await db.get_nick(user_id, chat_id)
        user_to_word = await db.get_user(user_id, chat_id)
        user_mention = f'<a href="https://t.me/{user_to_word.username}">{user_to_word_nick}</a>'

        if len(text) < 3:
            await message.reply('Неверный формат команды. Используйте: /command Add|Remove слово')
            return

        command = text[1].lower()
        word = text[2].lower().strip()

        if command == 'add':
            if user_to_word.rank >= 3:
                await db.add_filter_word(chat_id, word)
                await message.reply(f'Слово(а) "{word}" добавлено в фильтр.')
            else:
                await message.reply('Вы не можете использовать эту команду.')

        elif command == 'remove':
            if user_to_word.rank >= 3:
                success = await db.remove_filter_word(chat_id, word)
                if success:
                    await message.reply(f'Слово(а) "{word}" удалено из фильтра.')
                else:
                    await message.reply(f'Слово(а) "{word}" отсутствует в фильтре.')
            else:
                await message.reply('Вы не можете использовать эту команду.')

        else:
            await message.reply('Неверная команда. Используйте "Add" или "Remove".')


class FilterWordsList:
    @staticmethod
    async def filter_list(message: Message, bot: Bot):
        chat_id = message.chat.id
        user_id = message.from_user.id  # Получение user_id пользователя

        # Получение ника пользователя для упоминания в сообщении
        user_to_word_nick = await db.get_nick(user_id, chat_id)
        user_to_word = await db.get_user(user_id, chat_id)
        

        if user_to_word.rank >= 0:
            filter_words = await db.get_filter_words(chat_id)
            if filter_words:
                word_list = '\n'.join(filter_words)
                await message.reply(f'Список фильтрованных слов:\n{word_list}\n\nЕсли вы хотите добавить новые слова-обязательно записывайте их через запятую: огурец, салат')
            else:
                await message.reply('Список фильтрованных слов пуст.')
        else:
            await message.reply('Вы не можете использовать эту команду.')
        

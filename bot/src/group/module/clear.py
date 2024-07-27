
from aiogram import Bot
from aiogram.types import Message


from aiogram.exceptions import TelegramAPIError, DetailedAiogramError, TelegramNotFound
from src.group.request import DatabaseGroup
from src.group.module.other_functions import RankToUser

from aiogram.utils.markdown import hlink


r = RankToUser()
db = DatabaseGroup()


class ClearMessage:
    @staticmethod
    async def clear(message: Message, bot: Bot):
        chat_id = message.chat.id
        user_id = message.from_user.id

        parts = message.text.split()

        try:
            count = int(parts[1])
        except (IndexError, ValueError):
            await message.reply('Неправильный формат. Пожалуйста, укажите количество сообщений для удаления.')
            return
        
        user_rank = await db.get_user_rank(user_id, chat_id)

        # Проверяем права пользователя
        if int(user_rank) >= 1:
            deleted_count = 0
            # Удаляем сообщения в цикле
            try:
                for i in range(message.message_id - 1, message.message_id - count - 1, -1):
                    try:
                        await bot.delete_message(chat_id, i)
                        deleted_count += 1
                    except TelegramNotFound:
                        # Сообщение уже удалено, пропускаем
                        continue
                    except TelegramAPIError as e:
                        # Обработка ошибки API Telegram
                        continue  # Продолжаем удаление остальных сообщений
                p = await r.rank_(user_id, chat_id)
                user_nick = await db.get_nick(message.from_user.id, chat_id)
                user_info = await db.get_user(message.from_user.id, chat_id)
                user_link = hlink(f'{user_nick}' if user_nick else f'{user_info.username}', f'https://t.me/{user_info.username}')
                await message.reply(f'<b>{p}</b> {user_link} удалил {deleted_count} последних сообщений в группе.',
                                    parse_mode='html', disable_web_page_preview=True)
            except Exception as e:
                await message.reply(f'Произошла ошибка при удалении сообщений: {e}')
        else:
            await message.reply('У вас нет прав для использования этой команды.')
            


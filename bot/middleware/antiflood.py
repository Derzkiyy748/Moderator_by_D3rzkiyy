from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, ChatMember
from aiogram.types.chat_member_administrator import ChatMemberAdministrator
from aiogram.types.chat_member_owner import ChatMemberOwner

from src.group.request import DatabaseGroup

from cachetools import TTLCache

db = DatabaseGroup()

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, message_limit: int = 5, time_limit: int = 60) -> None:
        self.message_limit = message_limit
        self.time_limit = time_limit
        
        self.cache = TTLCache(maxsize=10_000, ttl=self.time_limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.type == 'private':
            return await handler(event, data)
        
        user_id = event.from_user.id
        chat_id = event.chat.id

         # Проверяем права бота
        bot: Bot = data['bot']
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        if bot_member.status not in ['administrator', 'creator']:
            await event.reply("У меня нет прав администратора. Пожалуйста, выдайте мне права администратора.")
            return
        
        # Получаем текущее количество сообщений пользователя из кеша
        message_count = self.cache.get(user_id, 0)

        # Получаем лимит сообщений из базы данных
        limit = await db.get_limit_message(chat_id)

        # Устанавливаем значение по умолчанию, если limit is None
        if limit is None:
            limit = self.message_limit

        if message_count >= limit:
            # Если превышен лимит сообщений, просто игнорируем сообщение
            await event.answer("Слишком много сообщений! Подождите немного.")
            return
        else:
            # Увеличиваем количество сообщений на 1
            self.cache[user_id] = message_count + 1
            return await handler(event, data)


        
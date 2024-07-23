from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import Message


'''class IsModerator(BaseFilter):
    key = 'is_moderator'

    def __init__(self, priority_threshold: int = 1):
        self.priority_threshold = priority_threshold

    async def check(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_priority = await self.get_user_priority(user_id, message.chat.id)
        return user_priority is not None and user_priority >= self.priority_threshold

    async def get_user_priority(self, user_id: int, chat_id: int) -> int:
        # Здесь вы должны реализовать логику получения приоритета пользователя.
        # Например, запрос к базе данных.
        # В этом примере я просто возвращаю приоритет 1 для демонстрации.
        # Замените это на ваш реальный код для получения приоритета пользователя.
        user_data = await DB.get_user(user_id, chat_id)  # Предполагается, что у вас есть метод для получения данных пользователя из базы
        if user_data:
            return user_data.get('priority', 0)
        return 0'''
        

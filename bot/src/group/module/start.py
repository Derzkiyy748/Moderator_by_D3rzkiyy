from aiogram import Bot

from aiogram.types import Message, CallbackQuery

from aiogram.filters import CommandObject

from src.group.request import DatabaseGroup


db = DatabaseGroup()

class StartBot:

    @staticmethod
    async def start(message: Message, bot: Bot, command: CommandObject | None = None):
        if await db.registered_chats(message.chat.id, message.chat.title):
            await bot.send_message(message.chat.id, "Привет, я бот для управления группой!\nДанная группа уже зарегистрирована")
        else:
            await bot.send_message(message.chat.id, "Привет, я бот для управления группой!\nДанная группа успешно зарегистрирована")

        
    @staticmethod
    async def add_usere(msg: Message, bot: Bot, command: CommandObject | None = None):
        await db.add_user(msg.from_user.id, msg.chat.id, msg.from_user.username, bot)
            







        
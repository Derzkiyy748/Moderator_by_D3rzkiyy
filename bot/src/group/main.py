from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart


from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from src.group.module.start import StartBot


class UserRouter:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.router = Router()
        self.router.message.filter(F.chat.type.in_({"group", "supergroup"}))
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self._add_user, F.text)
        self.router.message.register(self.start_command, Command("start"))

    async def start_command(self, message: Message):
        await StartBot.start(message, self.bot)

    async def _add_user(self, message: Message):
        await StartBot.add_usere(message, self.bot)



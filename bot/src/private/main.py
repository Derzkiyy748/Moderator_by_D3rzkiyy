from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from src.private.module.start import StartPrivate
from src.private.module.admin import Admin, AdminStates



class UserRouterPrivate:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.router = Router()
        self.router.message.filter(F.chat.type.in_({"private"}))
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self._start_command, Command("start"))

        self.router.message.register(self._admin_command, Command("admin"))
        self.router.callback_query.register(self._handle_callback, F.data == "mailing_group")
        self.router.callback_query.register(self._handle_callback, F.data == "mailing_private")
        self.router.message.register(self._cancel_mailing, F.text == "Отмена")

        self.router.message.register(self._admin_chats, F.text,  AdminStates.waiting_for_group_mailing)
        self.router.message.register(self._admin_private, F.text,  AdminStates.waiting_for_private_mailing)
    
    async def _start_command(self, message: Message):
        await StartPrivate.start_p(message)
    
    async def _admin_command(self, message: Message):
        await Admin.admin(message, self.bot)

    async def _admin_chats(self, message: Message, state: FSMContext):
        await Admin.send_group_mailing(message, self.bot, state)
    
    async def _admin_private(self, message: Message, state: FSMContext):
        await Admin.send_private_mailing(message, self.bot, state)

    async def _handle_callback(self, query: CallbackQuery, state: FSMContext):
        await Admin.handle_callback(query, self.bot, state)

    async def _cancel_mailing(self, message: Message, state: FSMContext):
        await Admin.cancel_mailing(message, self.bot, state)


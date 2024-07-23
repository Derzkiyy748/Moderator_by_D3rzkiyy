import asyncio
import logging
import sys
import os
import time

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from database.models import asyn_main
from misc.config import ADMIN_ID, LOG_CHANNEL_ID  # Убедитесь, что LOG_CHANNEL_ID добавлен в конфигурацию

from src.group.main import UserRouter

load_dotenv(dotenv_path="bot/misc/.env")

class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot: Bot, log_channel_id: int):
        super().__init__()
        self.bot = bot
        self.log_channel_id = log_channel_id

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.run_coroutine_threadsafe(self.send_log(log_entry), asyncio.get_event_loop())

    async def send_log(self, log_entry):
        await self.bot.send_message(chat_id=self.log_channel_id, text=log_entry)

class MyBot:
    def __init__(self):
        self.token = os.getenv('TOKEN_BOT')
        self.bot = Bot(self.token)
        self.dp = Dispatcher()  # Передача бота в диспетчер

        self.user_router = UserRouter(self.bot)
        self.dp.include_router(self.user_router.router)

    async def on_startup(self):

        # Вызов async_main для работы с базой данных
        await asyn_main()

        # Отправка сообщения администратору при запуске бота
        for admin_id in ADMIN_ID:
            await self.bot.send_message(chat_id=admin_id, text=f"Бот запущен \n<b>{time.asctime()}</b>", parse_mode='html')

    
        # Запуск диспетчера
        await self.dp.start_polling(self.bot)

    def run(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)  # Настройка уровня логирования

        # Создание и настройка логгера
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Создание и добавление пользовательского обработчика логов
        telegram_handler = TelegramLogsHandler(self.bot, LOG_CHANNEL_ID)
        telegram_handler.setLevel(logging.ERROR)  # Отправка только ошибок
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        telegram_handler.setFormatter(formatter)
        logger.addHandler(telegram_handler)

        try:
            asyncio.run(self.on_startup())  # Запуск асинхронной функции on_startup
        except KeyboardInterrupt:
            print("Exit")

if __name__ == "__main__":
    bot_instance = MyBot()
    bot_instance.run()









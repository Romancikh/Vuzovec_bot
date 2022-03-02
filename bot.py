import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import load_config
from app.handlers.question import register_handlers_question
from app.handlers.common import register_handlers_common
from app.handlers.control import register_handlers_control

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/test", description="Начать тест"),
        BotCommand(command="/stop", description="Завершить тест"),
        BotCommand(command="/info", description="Ссылки и полезная информация"),
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/back", description="На шаг назад")
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    config = load_config("config/bot.ini")
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_question(dp)
    register_handlers_control(dp)
    await set_commands(bot)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())

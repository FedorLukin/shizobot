from bot.handlers import main_handlers, admin_panel
from bot.config import env_vars

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode


bot = Bot(env_vars['BOT_TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_routers(admin_panel.router, main_handlers.router)
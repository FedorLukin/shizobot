from bot.handlers import main_handlers, admin_panel

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from decouple import config

# redis_url = f'://{config('REDIS_USER')}:{config('REDIS_PASSWORD')}@{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT')}/{config('REDIS_DB_NUM', default='0')}'
redis_url = 'redis://localhost:6379/0'
bot = Bot(config('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = RedisStorage.from_url(redis_url)
dp = Dispatcher(storage=storage)
dp.include_routers(admin_panel.router, main_handlers.router)
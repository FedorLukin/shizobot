import logging
from aiohttp import web

from bot.db.requests import get_admins
from bot.create_bot import bot, dp

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram import Bot

from decouple import config


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{config('BASE_WEBHOOK_URL')}{config('WEBHOOK_PATH')}", secret_token=config('WEBHOOK_SECRET'))
    admins_ids = await get_admins()
    for id in admins_ids:
        try:
            await bot.send_message(chat_id=id, text='Бот запущен 🚀')
        except (TelegramForbiddenError, TelegramBadRequest):
            pass


async def on_shutdown(bot: Bot) -> None:
    admins_ids = await get_admins()
    for id in admins_ids:
        try:
            await bot.send_message(chat_id=id, text='<b><i>Бот остановлен ❗</i></b>')
        except (TelegramForbiddenError, TelegramBadRequest):
            pass


def main() -> None:
    dp.shutdown.register(on_shutdown)
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config('WEBHOOK_SECRET'),
    )
    webhook_requests_handler.register(app, path=config('WEBHOOK_PATH'))
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=config('WEB_SERVER_HOST'), port=config('WEB_SERVER_PORT'))


if __name__ == "__main__":
    logs_format = '%(asctime)s - %(filename)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.ERROR, filename='logs.log', filemode='w', format=logs_format)
    main()

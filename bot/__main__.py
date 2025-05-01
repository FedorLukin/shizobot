import logging
import ssl
from aiohttp import web

from bot.db.requests import get_admins
from bot.create_bot import bot, dp
from bot.config import load_server_config

from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest


serv_conf = load_server_config()


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{serv_conf.base_webhook_url}{serv_conf.webhook_path}",
                          secret_token=serv_conf.webhook_secret)
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
            await bot.send_message(chat_id=id, text='<b><i>Бот остановлен ❗️</i></b>')
        except (TelegramForbiddenError, TelegramBadRequest):
            pass


def main() -> None:
    dp.shutdown.register(on_shutdown)
    dp.startup.register(on_startup)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=serv_conf.webhook_secret,
    )
    webhook_requests_handler.register(app, path=serv_conf.webhook_path)
    setup_application(app, dp, bot=bot)
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(serv_conf.webhook_ssl_cert, serv_conf.webhook_ssl_priv)
    web.run_app(app, host=serv_conf.web_server_host, port=serv_conf.web_server_port, ssl_context=context)


if __name__ == "__main__":
    logs_format = '%(asctime)s - %(filename)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.ERROR, filename='logs.log', filemode='w', format=logs_format)
    main()
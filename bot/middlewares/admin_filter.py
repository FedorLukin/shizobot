from aiogram.types import Message
from aiogram import BaseMiddleware

from typing import Any, Awaitable, Callable, Dict

from bot.db.requests import is_admin


class AdminAccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not await is_admin(message.from_user.id):

            return None

        return await handler(message, data)
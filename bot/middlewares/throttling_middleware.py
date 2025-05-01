from typing import Any, Awaitable, Callable, Dict
from cachetools import TTLCache
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


CACHE = TTLCache(maxsize=1000, ttl=1)


class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any | None:

        user_id = message.from_user.id
        current_count = CACHE.get(user_id, 0)

        if current_count > 2:
            return None

        CACHE[user_id] = current_count + 1

        if current_count == 2:
            await message.answer(text='подождите 5 секунд и повторите запрос')
            return

        return await handler(message, data)
import asyncio
from typing import Any, Dict, Union, Callable

from aiogram.types import Message
from aiogram import BaseMiddleware


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.15):
        self.latency = latency
        self.album_data = {}

    def collect_album_messages(self, event: Message) -> int:
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = {"messages": []}

        self.album_data[event.media_group_id]["messages"].append(event)

        return len(self.album_data[event.media_group_id]["messages"])

    async def __call__(self, handler: Callable, event: Message, data: Dict[str, Any]) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        total_before = self.collect_album_messages(event)
        await asyncio.sleep(self.latency)
        album_messages = self.album_data.get(event.media_group_id)

        if album_messages is None:
            return

        total_after = len(album_messages["messages"])
        if total_before != total_after:
            return

        album_messages["messages"].sort(key=lambda x: x.message_id)
        data["album"] = album_messages["messages"]
        del self.album_data[event.media_group_id]

        return await handler(event, data)
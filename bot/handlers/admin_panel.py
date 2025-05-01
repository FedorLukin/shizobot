from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import StateFilter, Command
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram import Bot, Router, F

from bot.keyboards.admin_panel_keyboards import *

from bot.middlewares.album_middleware import AlbumMiddleware
from bot.middlewares.admin_filter import AdminAccessMiddleware

from bot.misc.states import AdminPanelStates

# from bot.db.requests import get_users, delete_user, get_rates, set_rate, get_orders
# from bot.db.requests import get_products_list, set_product_status, get_product_status
from bot.db.requests import *
import logging
import datetime as dt
import asyncio

router = Router()
router.message.middleware(AdminAccessMiddleware())
router.message.middleware(AlbumMiddleware())
router.callback_query.middleware(AdminAccessMiddleware())



@router.message(Command('admin'))
async def admin(message: Message) -> None:
    await message.answer(text=f'Здравствуйте, {message.from_user.first_name}! Вы являетесь администратором '
                              f'данного бота и можете воспользоваться админ-панелью', reply_markup=admin_panel_kb())


@router.message(F.text == 'админ-панель 🔐')
async def admin_panel(message: Message, state: FSMContext) -> None:
    await message.answer(text='Добро пожаловать в админ-панель!', reply_markup=admin_panel_kb())
    await state.clear()


@router.callback_query(F.data == 'back')
async def admin_panel_back(callback: CallbackQuery, state: FSMContext) -> None:
    notification_data = await state.get_data()
    messages_to_delete = notification_data.get('to_delete')
    if isinstance(messages_to_delete, Message):
        await messages_to_delete.delete()
    elif messages_to_delete:
        for message in messages_to_delete:
            await message.delete()
    if callback.message.content_type == ContentType.TEXT:
        await callback.message.edit_text(text='Добро пожаловать в админ-панель!',
                                         reply_markup=admin_panel_kb(callback.from_user.id))
    else:
        await callback.message.delete()
        await callback.message.answer(text='Добро пожаловать в админ-панель!',
                                      reply_markup=admin_panel_kb(callback.from_user.id))
    await state.clear()


@router.callback_query(F.data == 'start_notification')
async def notification_message_request(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminPanelStates.message_request)
    await callback.message.edit_text(text='отправьте сообщение для дальнейшей рассылки',
                                     reply_markup=back_to_admin_kb())


@router.message(StateFilter(AdminPanelStates.message_request))
async def notification_message_confirm(message: Message, state: FSMContext, album: list = None) -> None:
    if album:
        notification_text = album[0].caption if album[0].caption else ''
        album_builder = MediaGroupBuilder(caption=notification_text)

        for ms in album:
            if ms.photo:
                album_builder.add_photo(media=ms.photo[0].file_id)
            elif ms.video:
                album_builder.add_video(media=ms.video.file_id)

        album = album_builder.build()
        msg = await message.answer_media_group(media=album)
        await state.update_data(to_delete=msg, contains_album=True, file_id=album)
        await message.answer(text='<i>Подтвердите отправку сообщения</i>', reply_markup=notification_confirmation_kb())

    else:
        await state.update_data(notification_message=message)
        if message.content_type == ContentType.VIDEO_NOTE:
            msg = await message.send_copy(chat_id=message.from_user.id)
            await state.update_data(to_delete=msg, file_id=message.video_note.file_id)
            await message.answer(text='<i>Подтвердите отправку сообщения</i>',
                                 reply_markup=notification_confirmation_kb())
        elif message.content_type in (ContentType.TEXT, ContentType.PHOTO, ContentType.VIDEO,
                                      ContentType.DOCUMENT, ContentType.VOICE):
            await message.send_copy(chat_id=message.from_user.id, reply_markup=notification_confirmation_kb())
        else:
            await message.answer(text='<i>Неподдерживаемый тип сообщения</i>')

    await state.set_state(AdminPanelStates.notification_start)


@router.callback_query(F.data == 'send', StateFilter(AdminPanelStates.notification_start))
async def notifaction_start(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    notification_data = await state.get_data()

    messages_to_delete = notification_data.get('to_delete')
    await callback.message.delete()

    if isinstance(messages_to_delete, Message):
        await messages_to_delete.delete()
    elif messages_to_delete:
        for message in messages_to_delete:
            await message.delete()
    msg = await callback.message.answer(text='рассылка в процессе\n' + '⬜️' * 10)
    recievers = await get_users()
    rows_num = len(recievers)
    notification_message = notification_data.get('notification_message')
    for counter, user_id in enumerate(recievers, start=1):
        try:
            if notification_data.get('contains_album'):
                await bot.send_media_group(chat_id=user_id, media=notification_data['file_id'])
            else:
                await notification_message.send_copy(user_id)

        except TelegramForbiddenError:
            await delete_user(user_id)

        percent = int(counter / rows_num * 100) // 10
        await msg.edit_text(text=f'рассылка в процессе\n{"🟩" * percent}{"⬜️" * (10 - percent)} {counter}/{rows_num}')

        await asyncio.sleep(0.035)

    await msg.edit_text(text='Рассылка завершена✅')


@router.callback_query(F.data == 'stats')
async def get_stats(callback: CallbackQuery) -> None:
    ankets = await get_ankets_data()
    ages = [anket[1] for anket in ankets]
    middle_age = round(sum(ages) / len(ages))
    await callback.message.answer(text=f'<b><i>Статистика пользователей бота:</i></b>\nВсего анкет: <b>{len(ankets)}</b>, из них <b>{sum(1 for anket in ankets if not anket[0])}</b> тянок и <b>{sum(1 for anket in ankets if anket[0])}</b> мужла\nАктивных анкет: <b>{sum(1 for anket in ankets if anket[3])}</b>, из них <b>{sum(1 for anket in ankets if not anket[0] and anket[3])}</b> тянок и <b>{sum(1 for anket in ankets if anket[0] and anket[3])}</b> мужла\nСредний возраст анкеты: <b>{middle_age}</b> лет\nКоличество уникальных указанных городов: <b>{len({anket[2] for anket in ankets if anket[2]})}</b>')
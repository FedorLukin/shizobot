from aiogram.fsm.context import FSMContext
# from aiogram.dispatcher import StorageKey

from aiogram.filters import ChatMemberUpdatedFilter, LEFT, StateFilter, Command, KICKED
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated, ReplyKeyboardRemove, Location, ContentType
from aiogram import Router, F, Bot
from aiogram.utils.media_group import MediaGroupBuilder
from bot.keyboards.main_keyboards import *
from bot.keyboards.admin_panel_keyboards import *
from bot.middlewares.throttling_middleware import ThrottlingMiddleware
from bot.db.requests import *
from bot.misc.states import RegistrationSteps, MainStates
from bot.misc.gecoder import get_city_by_name, get_city_by_cords
# from bot.create_bot import dp
import logging
import datetime as dt
from typing import Iterator


router = Router()
router.message.middleware(ThrottlingMiddleware())


async def start_search(message: Message, state: FSMContext) -> None:
    """Старт поиска анкет"""
    await state.set_state(MainStates.search)
    await message.answer('🔎✨', reply_markup=search_kb())
    await show_next_anket(message=message, state=state)


async def show_next_anket(message: Message, state: FSMContext) -> None:
    """Просмотр следующей анкеты"""
    anket_id = await get_anket_from_queue(message.from_user.id, state)
    if anket_id:
        await render_anket(anket_id, message)
        await state.update_data(processing=anket_id)


async def show_self_anket(message: Message, state: FSMContext) -> None:
    """"Рендер анкеты пользователя и выбор дальнейшего действия"""
    await state.set_state(MainStates.edit_anket_or_start)
    await message.answer(text='Так выглядит твоя анкета:')
    await render_anket(message.from_user.id, message)
    await message.answer('1. Смотреть анкеты.\n2. Заполнить анкету заново.\n3. Изменить фото/видео.\n4. Изменить текст анкеты.', reply_markup=main_options_kb())


async def render_anket(anket_id, message: Message, pre_text='', after_text='') -> None:
    """Рендер анкеты"""
    anket = await get_anket(anket_id)
    media_list = await get_media(anket_id)
    city = f', {anket.city}' if anket.city else ''
    anket_text = f'{pre_text}{anket.name}, {anket.age}{city} - {anket.description}{after_text}'
    if media_list[0].video:
        await message.answer_video(video=media_list[0].file, caption=anket_text)
    else:
        album_builder = MediaGroupBuilder(caption=anket_text)
        for media in media_list:
            album_builder.add_photo(media=media.file)
        album = album_builder.build()
        await message.answer_media_group(media=album, caption=anket_text, )


async def get_anket_from_queue(tg_id: int, state: FSMContext) -> int | None:
    """Получение следующей анкеты из стека"""
    data = await state.get_data()
    queue, offset = data['queue'], data['offset']
    try: # пробуем получить анкету из итератора
        return next(queue)

    except StopIteration: # если стек исчерпан
        offset += 1 # увеличиваем смещение на 1

        for i in offset, 0: # пробуем найти анкеты в бд с увеличенным или нулевым смещением
            ankets = await get_ankets_queue(tg_id, i)
            if ankets:
                await state.update_data(queue=iter(ankets), offset=i)
                data = await state.get_data()
                return next(data['queue'])

        return None # возвращаем None если анкет не найдено


@router.message(Command('start'))
async def start(message: Message, state: FSMContext) -> None:
    """Старт бота или вызов главного меню"""
    if not await get_anket(message.from_user.id):
        await state.clear()
        await state.set_state(RegistrationSteps.start)
        await message.answer('добро пожаловать в клуб знакомств шизоцелов!', reply_markup=start_bot_kb())
    else:
        await menu(message, state)


@router.message(Command('menu'))
async def menu(message: Message, state: FSMContext) -> None:
    """Меню выбора основных опций"""
    if await get_anket(message.from_user.id):
        await state.set_state(MainStates.option_selection)
        await message.answer('1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n4. Донат админу',
                             reply_markup=main_options_kb())
    else:
        await start(message=message, state=state)


@router.message(F.text == 'начать', StateFilter(RegistrationSteps.start))
async def age_request(message: Message, state: FSMContext) -> None:
    """Старт регистрации, запрос возраста"""
    if message.from_user.username:
        await state.set_state(RegistrationSteps.age_request)
        await message.answer('Сколько тебе лет?', reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(text='Сделай доступным свой юзернейм и попробуй снова')


@router.message(StateFilter(RegistrationSteps.age_request))
async def gender_request(message: Message, state: FSMContext) -> None:
    """Проверка валидности возраста, запрос пола"""
    if not message.text.strip().isdigit() or int(message.text) not in range(14, 60):
        await message.answer('<b>Введи корректное число!</b>')
    else:
        await state.update_data(age=int(message.text.strip()))
        await state.set_state(RegistrationSteps.gender_request)
        await message.answer('Кем себя ощущаешь?', reply_markup=gender_selection_kb())


@router.message(F.text.in_(('инцел', 'фемцел')), StateFilter(RegistrationSteps.gender_request))
async def interest_request(message: Message, state: FSMContext) -> None:
    """Уточнение интереса"""
    await state.update_data(gender=message.text == 'инцел')
    await state.set_state(RegistrationSteps.interest_request)
    await message.answer('А кого хочешь найти?', reply_markup=interest_selection_kb())


@router.message(F.text.in_(('фемцелочку', 'инцела', 'да похуй')), StateFilter(RegistrationSteps.interest_request))
async def location_request(message: Message, state: FSMContext) -> None:
    """Запрос города"""
    await state.update_data(interest=('фемцелочку', 'инцела', 'да похуй').index(message.text))
    await state.set_state(RegistrationSteps.location_request)
    await message.answer('Окей, напиши свой город или отправь геопозицию, чтобы найти шизов рядом', reply_markup=location_request_kb())


@router.message(F.content_type.in_({'text', 'location'}), StateFilter(RegistrationSteps.location_request))
async def name_request(message: Message, state: FSMContext) -> None:
    """Проверка города и запрос имени"""
    city_name = None
    if message.content_type == ContentType.LOCATION:
        msg = await message.answer(text='<i>Идёт доксинг...</i>', reply_markup=ReplyKeyboardRemove())
        latitude, longitude = message.location.latitude, message.location.longitude
        city_name = await get_city_by_cords(latitude, longitude)
        await msg.reply(text='<b>Успешно сватнул адрес!</b>') if city_name else await message.answer(text='Что-то пошло не так, будем считать что у тебя нет города.')

    elif message.text != 'пропустить ⏩':
        msg = await message.answer(text='<i>Идёт доксинг...</i>', reply_markup=ReplyKeyboardRemove())
        city_name = await get_city_by_name(message.text.strip())
        await msg.reply(text='<b>Пополнил базы osint ботов!</b>') if city_name else await message.answer(text='Что-то пошло не так, будем считать что у тебя нет города.')

    await state.update_data(city=city_name)
    await state.set_state(RegistrationSteps.name_request)
    await message.answer(text='Как мне к тебе обращаться?', reply_markup=ReplyKeyboardRemove())


@router.message(F.text, StateFilter(RegistrationSteps.name_request))
async def description_request(message: Message, state: FSMContext) -> None:
    """Проверка валидности имени и запрос текста анкеты"""
    if len(message.text) <= 32:
        await state.update_data(name=message.text.strip())
        await state.set_state(RegistrationSteps.description_request)
        await message.answer(text='Красивое имя, у меня аж встал) Теперь расскажи о себе и желательно в деталях.')
    else:
        await message.answer(text='Чёт сильно длинное у тебя имя, я не запомню, попробуй ещё раз.')


@router.message(F.text, StateFilter(RegistrationSteps.description_request))
async def media_request(message: Message, state: FSMContext) -> None:
    """Проверка валидности текста анкеты и запрос медиа"""
    if len(message.text) <= 2048:
        await message.answer(text='Отлично, теперь пришли фото или видео')
        await state.update_data(description=message.text.strip(), media=[])
        await state.set_state(RegistrationSteps.media_confirmation)
    else:
        await message.answer(text='А не дохуя-ли информации? Давай покороче как-то, пробуй ещё раз.')


@router.message(F.content_type.in_({'photo', 'video', 'text'}), StateFilter(RegistrationSteps.media_confirmation))
async def media_confirmation(message: Message, state: FSMContext) -> None:
    """Сохранение медиа"""
    data = await state.get_data()
    if message.content_type == ContentType.VIDEO and not data.get('media'):
        if not data.get('editing_media'):
            await state.update_data(media=message.video.file_id, video=True)
            await anket_confirmation(message=message, state=state)
        else:
            await add_media(tg_id=message.from_user.id, media=[message.video.file_id], is_video=True)
            await show_self_anket(message=message, state=state)

    elif message.content_type == ContentType.PHOTO:
        data['media'].append(message.photo[-1].file_id)
        if len(data['media']) < 3:
            await message.answer(text=f'Фото добавлено {len(data['media'])} из 3. Добавить ещё?', reply_markup=add_photo_confirmation_kb())
        else:
            await state.update_data(video=False)
            await anket_confirmation(message=message, state=state)

    elif message.content_type == ContentType.TEXT:
        if message.text == 'это все, сохранить фото':
            if not data.get('editing_media'):
                await state.update_data(video=False)
                await anket_confirmation(message=message, state=state)
            else:
                await add_media(tg_id=message.from_user.id, media=data['media'], is_video=False)
                await show_self_anket(message=message, state=state)


async def anket_confirmation(message: Message, state: FSMContext) -> None:
    """Подтверждение данных для анкеты"""
    data = await state.get_data()
    name_and_age = f'{data['name']}, {data['age']}' # формируем текст анкеты
    main_info = f'{name_and_age}, {data['city']}' if data['city'] else name_and_age
    description, media = data['description'], data['media']
    anket_text = f'{main_info} – {description}' 
    await message.answer(text='<i>Так выглядит твоя анкета:</i>')
    if not data['video']:
        album_builder = MediaGroupBuilder(caption=anket_text)
        for id in media:
            album_builder.add_photo(media=id)
        album = album_builder.build()
        await message.answer_media_group(media=album, reply_markup=anket_confirmation_kb())
    else:
        await message.answer_video(media=data['media'][0])
    await state.set_state(RegistrationSteps.anket_confirmation)
    await message.answer(text='Всё верно?', reply_markup=anket_confirmation_kb())


@router.message(F.text.in_(('да', 'изменить анкету')), StateFilter(RegistrationSteps.anket_confirmation))
async def anket_saving(message: Message, state: FSMContext) -> None:
    """Сохранение анкеты"""
    data = await state.get_data()
    status = message.text == 'да'
    await add_anket(tg_id=message.from_user.id, name=data['name'], age=data['age'], gender=data['gender'],
                    interest=data['interest'], city=data['city'], description=data['description'], status=status)
    await add_media(tg_id=message.from_user.id, media=data['media'], is_video=data['video'])
    await state.clear()
    
    await state.set_state(MainStates.edit_anket_or_start)
    await message.answer('1. Смотреть анкеты.\n2. Заполнить анкету заново.\n3. '
                        'Изменить фото/видео.\n4. Изменить текст анкеты.', reply_markup=main_options_kb())
        

@router.message(StateFilter(MainStates.subscription_check))
async def check_subscription(message: Message, state: FSMContext, bot: Bot):
    """Проверка подписки на канал"""
    if message.text == 'я подписался':
        member = await bot.get_chat_member(chat_id='@shizocells', user_id=message.from_user.id)
        if member.status == 'left':
            await message.answer(text='Ну вот кому ты пиздишь? Ты чо, типа, самый умный?')
        else:
            await state.set_state(MainStates.option_selection)
            await message.answer('1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n4. Донат админу', reply_markup=main_options_kb())


@router.message(F.text.in_(('1🚀', '2', '3', '4')), StateFilter(MainStates.edit_anket_or_start))
async def start_search_or_edit_anket(message: Message, state: FSMContext, bot: Bot) -> None:
    """Опции редактирования анкеты или старт поиска анкет"""
    match message.text:
        case '1🚀': # проверка подписки и старт поиска анкет 
            member = await bot.get_chat_member(chat_id='@shizocells', user_id=message.from_user.id)
            if member.status == 'left':
                await state.set_state(MainStates.subscription_check)
                await message.answer(text='Для использования бота необходимо быть подписанным на <a href="https://t.me/shizocells">канал</a>', reply_markup=subscribe_confirm())
            
            else:
                data = await state.get_data()
                await change_anket_status(message.from_user.id, True)

                if 'queue' in data.keys():
                    await start_search(message=message, state=state)

                else:
                    ankets_queue = await get_ankets_queue(message.from_user.id, 0)

                    if not ankets_queue:
                        await message.answer('Не нашёл подходящих анкет')
                        await message.answer('1. Смотреть анкеты.\n2. Заполнить анкету заново.\n3. '
                                            'Изменить фото/видео.\n4. Изменить текст анкеты.',
                                            reply_markup=main_options_kb())
                    else:
                        await state.update_data(queue=iter(ankets_queue), offset=0)
                        await start_search(message=message, state=state)

        case '2': # заполнение анкеты с начала
            await age_request(message=message, state=state)

        case '3': # изменение фото/видео анкеты
            await state.update_data(editing_media=True)
            await media_request(message=message, state=state)
        
        case '4': # редактирование текста анкеты
            await state.set_state(MainStates.description_edit)
            await message.answer(text='Расскажи о себе и желательно в деталях', reply_markup=back_kb())


@router.message(StateFilter(MainStates.description_edit))
async def anket_description_edit(message: Message, state: FSMContext) -> None:
    """Редактирование текста анкеты"""
    if message.text == 'назад':
        await show_self_anket(message=message, state=state)
    elif len(message.text) <= 2048:
        await change_anket_description(tg_id=message.from_user.id, text=message.text)
        await show_self_anket(message=message, state=state)
    else:
        await message.answer(text='А не дохуя-ли информации? Давай покороче как-то, пробуй ещё раз.')


@router.message(F.text.in_(('1🚀', '2', '3', '4')), StateFilter(MainStates.option_selection))
async def main_options(message: Message, state: FSMContext, bot: Bot) -> None:
    """Основные опции"""
    match message.text:
        case '1🚀': # проверка подписки и старт поиска анкет 
            member = await bot.get_chat_member(chat_id='@shizocells', user_id=message.from_user.id)
            if member.status == 'left':
                await state.set_state(MainStates.subscription_check)
                await message.answer(text='Для использования бота необходимо быть подписанным на <a href="https://t.me/shizocells">канал</a>', reply_markup=subscribe_confirm())
            
            else:
                data = await state.get_data()
                await change_anket_status(message.from_user.id, True)

                if 'queue' in data.keys():
                    await start_search(message=message, state=state)
                
                else:
                    ankets_queue = await get_ankets_queue(message.from_user.id, 0)
                    if ankets_queue:
                        await state.update_data(queue=iter(ankets_queue), offset=0)
                        await start_search(message=message, state=state)
                    
                    else:
                        await message.answer('Не нашёл подходящих анкет')
                        await message.answer('1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n4. Донат админу', reply_markup=main_options_kb())

        case'2': # показ анкеты пользователя
            await show_self_anket(message=message, state=state)

        case '3': # отключение анкеты
            await state.set_state(MainStates.anket_state_switch)
            await message.answer(text='Отключить анкету? Так ты не узнаешь, что кому-то не похуй на тебя.',
                                 reply_markup=turn_anket_off_kb())

        case '4': # донат
            await message.answer(text='кидай бабки сюда: <code>1234567890</code>')


@router.message(F.text.in_(('❤️', '💌', '👎', '💤')), StateFilter(MainStates.search))
async def search(message: Message, state: FSMContext, bot: Bot) -> None:
    """Оценка анкет"""
    match message.text:
        case '👎': await show_next_anket(message, state) # дизлайк

        case '❤️': # лайк
            data = await state.get_data()
            if await check_anket_status(tg_id=data['processing']):
                if not await save_like(message.from_user.id, username=message.from_user.username, anket_id=data['processing']):
                    await bot.send_message(chat_id=data['processing'], text='Кому-то понравилась твоя анкета', reply_markup=likes_watch_kb())
                await show_next_anket(message, state)

        case '💌': # сообщение
            await state.set_state(MainStates.message_request)
            await message.answer('Напиши сообщение для этого пользователя', reply_markup=back_kb())

        case '💤': # возврат в меню
            await state.set_state(MainStates.option_selection)
            await message.answer('Подождём пока твою анкету кто-то увидит')
            await message.answer('1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n4. Донат админу', reply_markup=main_options_kb())


@router.message(F.text == 'посмотреть')
async def search(message: Message, state: FSMContext) -> None:
    """Просмотр анкет людей, которым понравился пользователь"""
    likes = await get_likes(message.from_user.id)
    likes_queue = iter(likes)
    try:
        like = next(likes_queue)
        await message.answer(text='🔎📑', reply_markup=likes_dislike_kb())
        pre_text = '<b>Кому-то понравилась твоя анкета</b>'
        pre_text += f'(и ещё {len(likes) - 1})\n\n' if len(likes) > 1 else '\n\n'
        after_text = f'\n\n💌 <b><i>Сообщение для тебя:</i></b>\n{like.message}' if like.message else ''
        await render_anket(like.sender_id, message, pre_text, after_text)
        await state.update_data(processing=like)
        await state.set_state(MainStates.likes_answer)
        await state.update_data(likes=likes_queue, count=len(likes) - 1)

    except StopIteration:
        await message.answer(text='Уже неакутально 😔')
        await menu(message=message, state=state)


@router.message(F.text.in_(('❤️', '👎')), StateFilter(MainStates.likes_answer))
async def like_answer(message: Message, state: FSMContext, bot: Bot) -> None:
    """Ответ на лайки"""
    data = await state.get_data()

    if message.text == '❤️':
        anket = await get_anket(tg_id=data['processing'].sender_id)
        await message.answer(text=f'Отлично, начинай общаться с <a href="https://t.me/{data['processing'].sender_username}">{anket.name}</a>.', disable_web_page_preview=True)
        sender_name = await get_name(tg_id=message.from_user.id)
        await bot.send_message(data['processing'].sender_id, text=f'Есть взаимная симпатия, начинай общаться с <a href="https://t.me/{message.from_user.username}">{sender_name}</a>.', reply_markup=call_menu_kb(), disable_web_page_preview=True)

    await remove_like(data['processing'])

    try:
        like = next(data['likes'])
        pre_text = '<b>Кому-то понравилась твоя анкета</b>'
        pre_text += f'(и ещё {data['count'] - 1})\n\n' if data['count'] >= 2 else '\n\n'
        after_text = f'\n\n💌 <b><i>Сообщение для тебя:\n{like.message}</b></i>' if like.message else ''
        await state.update_data(count=data['count'] - 1, processing=like)
        await render_anket(like.sender_id, message, pre_text, after_text)

    except StopIteration:
        await state.clear()
        await state.set_state(MainStates.option_selection)
        await message.answer('1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n4. Донат админу', reply_markup=main_options_kb())


@router.message(F.text, StateFilter(MainStates.message_request))
async def message_request(message: Message, state: FSMContext, bot: Bot) -> None:
    """Отправка сообщения симпатии"""
    data = await state.get_data()

    if message.text == 'назад':
        await state.set_state(MainStates.search)
        await message.answer(text='🔎✨', reply_markup=search_kb())
        await render_anket(data['processing'], message)

    else:
        if not await save_like(message.from_user.id, message.from_user.username, data['processing'], message.text):
            await bot.send_message(chat_id=data['processing'], text='Кому-то понравилась твоя анкета', reply_markup=likes_watch_kb())
        await message.answer(text='Сообщение отправлено', reply_markup=search_kb())
        await state.set_state(MainStates.search)
        await show_next_anket(message, state)


@router.message(F.text, StateFilter(MainStates.anket_state_switch))
async def anket_state_switch(message: Message, state: FSMContext) -> None:
    """Отключение анкеты"""
    match message.text:
        case 'отключить анкету 😴':
            await change_anket_status(message.from_user.id, False)
            await message.answer('Профитроли айкос дарк рейв вписка, соли дабл мамонт - ору. Отключил анкету.',
                                reply_markup=turn_anket_on_kb())
            
        case 'включить анкету' | 'назад':
            await menu(message=message, state=state)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated) -> None:
    """Отключение анкеты при блокировке бота"""
    """
    Удаляет пользователя из базы данных, когда пользователь блокирует бота.

    Аргументы:
        event (ChatMemberUpdated): Событие обновления статуса пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await change_anket_status(tg_id=event.from_user.id, status=False)

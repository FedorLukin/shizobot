from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def start_bot_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='начать'))
    return kb.as_markup(resize_keyboard=True)


def gender_selection_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='девушка'))
    kb.add(KeyboardButton(text='парень'))
    return kb.as_markup(resize_keyboard=True)


def interest_selection_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='девушку'))
    kb.add(KeyboardButton(text='парня'))
    kb.add(KeyboardButton(text='всё равно'))
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def location_request_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='отправить геолокацию 📍', request_location=True))
    kb.add(KeyboardButton(text='пропустить ⏩'))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def add_photo_confirmation_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='это все, сохранить фото'))
    return kb.as_markup(resize_keyboard=True)


def anket_confirmation_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='да'))
    kb.add(KeyboardButton(text='изменить анкету'))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def main_options_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='1🚀'))
    kb.add(KeyboardButton(text='2'))
    kb.add(KeyboardButton(text='3'))
    kb.add(KeyboardButton(text='4'))
    return kb.as_markup(resize_keyboard=True)


def search_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='❤️'))
    kb.add(KeyboardButton(text='💌'))
    kb.add(KeyboardButton(text='👎'))
    kb.add(KeyboardButton(text='💤'))
    return kb.as_markup(resize_keyboard=True)


def likes_watch_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='посмотреть'))
    return kb.as_markup(resize_keyboard=True)


def likes_dislike_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='❤️'))
    kb.add(KeyboardButton(text='👎'))
    return kb.as_markup(resize_keyboard=True)


def back_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='назад'))
    return kb.as_markup(resize_keyboard=True)


def turn_anket_off_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='отключить анкету 😴'))
    kb.add(KeyboardButton(text='назад'))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def turn_anket_on_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='включить анкету'))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def subscribe_confirm() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='я подписался'))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def call_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='/menu'))
    return kb.as_markup(resize_keyboard=True)


def start_chat_kb(id: int, name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=name, url=f"tg://user?id={id}")
    return kb.as_markup(resize_keyboard=True)
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_panel_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='запустить рассылку ✉️', callback_data='start_notification')
    kb.button(text='статистика 📊', callback_data='stats')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_to_admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='назад', callback_data='back')
    return kb.as_markup(resize_keyboard=True)


def notification_confirmation_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='отмена', callback_data='back')
    kb.button(text='отправить', callback_data='send')
    kb.adjust(2)
    return kb.as_markup(resize_keyborad=True)
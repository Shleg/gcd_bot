import json
import urllib.parse

import emoji
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from database.data import DEFAULT_PHASES_DICT
from database.config_data import BOT_FORM


# Функция для создания inline клавиатуры выбора роли
def request_role() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('👩‍⚕️ Врач-реферал', callback_data='role:Врач-реферал'),
        InlineKeyboardButton('🔬 Врач-исследователь', callback_data='role:Врач-исследователь')
    )
    return keyboard


# Функция для создания клавиатуры с кнопкой "Получить контакт врача"
def request_doctor_contact(doctor_id):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Получить контакт врача-исследователя",
                                        callback_data=f"cont:"
                                                      f"{doctor_id}:")
    keyboard.add(button)
    return keyboard


def submit_request() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Да', callback_data='submit:yes'),
        InlineKeyboardButton('Нет', callback_data='submit:no')
    )
    return keyboard


def request_condition() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Стационар', callback_data='condition:1'),
        InlineKeyboardButton('Амбулатория', callback_data='condition:2')
    )
    return keyboard


def request_phase() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for phase in DEFAULT_PHASES_DICT.keys()[::-1]:
        keyboard.add(
            InlineKeyboardButton(phase, callback_data=f'phase:{phase}')
        )
    return keyboard


# def request_communication() -> InlineKeyboardMarkup:
#     keyboard = InlineKeyboardMarkup()
#     keyboard.add(
#         InlineKeyboardButton('Telegram', callback_data='comm:Telegram'),
#         InlineKeyboardButton('WhatsApp', callback_data='comm:WhatsApp')
#     )
#     keyboard.add(
#         InlineKeyboardButton('Телефон', callback_data='comm:Phone'),
#         InlineKeyboardButton('Почта', callback_data='comm:Email')
#     )
#     return keyboard


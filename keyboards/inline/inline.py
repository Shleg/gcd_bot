import json
import urllib.parse

import emoji
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from database.data import DEFAULT_PHASES_DICT, DEFAULT_CONDITION_DICT, DEFAULT_SPEC_DICT
from database.config_data import BOT_FORM
from utils.functions import clean_selected_specs, get_specs_list_from_wix


# Функция для создания inline клавиатуры выбора роли
def request_role() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('👩‍⚕️ Врач-реферал', callback_data='role:Врач-реферал'))
    keyboard.add(InlineKeyboardButton('🔬 Врач-исследователь', callback_data='role:Врач-исследователь'))
    return keyboard


def request_specialization(specializations, selected_specializations) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons_list = []

    for specialization in specializations:
        # Получаем текущее состояние выбора специализации
        is_selected = selected_specializations.get(specialization)

        # Создаем кнопку для каждой специализации с зеленой галочкой, если выбрана
        button_text = f"✅ {specialization}" if is_selected else specialization
        button = InlineKeyboardButton(button_text, callback_data=f'spec:{specialization}')
        buttons_list.append(button)

    for i in range(0, len(buttons_list), 2):
        keyboard.add(*buttons_list[i:i + 2])

    # Добавляем кнопку для подтверждения выбора
    confirm_button = InlineKeyboardButton("👍 Подтвердить выбор", callback_data="spec:confirm")
    keyboard.add(confirm_button)

    return keyboard


def request_city(cities, selected_cities) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons_list = []

    for city in cities:
        # Получаем текущее состояние выбора специализации
        is_selected = selected_cities.get(city)

        # Создаем кнопку для каждой специализации с зеленой галочкой, если выбрана
        button_text = f"✅ {city}" if is_selected else city
        button = InlineKeyboardButton(button_text, callback_data=f'city:{city}')
        buttons_list.append(button)

    for i in range(0, len(buttons_list), 2):
        keyboard.add(*buttons_list[i:i + 2])

        # Добавляем кнопку для подтверждения выбора
    confirm_button = InlineKeyboardButton("👍 Подтвердить выбор", callback_data="city:confirm")
    keyboard.add(confirm_button)

    return keyboard


def request_drugs(drugs, selected_drugs) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()


    for drug in drugs:
        # Получаем текущее состояние выбора специализации
        is_selected = selected_drugs.get(drug)

        # Создаем кнопку для каждой специализации с зеленой галочкой, если выбрана
        button_text = f"✅ {drug}" if is_selected else drug
        button = InlineKeyboardButton(button_text, callback_data=f'drug:{drug}')
        keyboard.add(button)

    # Добавляем кнопку для подтверждения выбора
    confirm_button = InlineKeyboardButton("👍 Подтвердить выбор", callback_data="drug:confirm")
    keyboard.add(confirm_button)

    return keyboard

# def request_area(specializations, selected_specializations) -> InlineKeyboardMarkup:
#     keyboard = InlineKeyboardMarkup(row_width=2)
#     buttons_list = []
#
#     for specialization in specializations:
#         # Получаем текущее состояние выбора специализации
#         is_selected = selected_specializations.get(specialization)
#
#         # Создаем кнопку для каждой специализации с зеленой галочкой, если выбрана
#         button_text = f"✅ {specialization}" if is_selected else specialization
#         button = InlineKeyboardButton(button_text, callback_data=f'spec:{specialization}')
#         buttons_list.append(button)
#
#     for i in range(2, len(buttons_list), 2):
#         keyboard.add(*buttons_list[i:i + 2])
#
#     # Добавляем кнопку для подтверждения выбора
#     confirm_button = InlineKeyboardButton("👍 Подтвердить выбор", callback_data="spec:confirm")
#     keyboard.add(confirm_button)
#
#     return keyboard

# Функция для создания клавиатуры с кнопкой "Получить контакт врача"
def request_doctor_contact(doctor_id):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("🔬 Получить контакт врача-исследователя",
                                        callback_data=f"cont:"
                                                      f"{doctor_id}:")
    keyboard.add(button)
    return keyboard


def submit_request() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('\U00002705 Да', callback_data='submit:yes'),
        InlineKeyboardButton('\U0000274C Нет', callback_data='submit:no')
    )
    return keyboard


def request_condition() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    condition = list(DEFAULT_CONDITION_DICT.keys())[::-1]
    keyboard.add(
        InlineKeyboardButton(f'\U0001F6CC  {condition[0]}', callback_data=f'condition:{condition[0]}'),
        InlineKeyboardButton(f'\U0001F6B6  {condition[1]}', callback_data=f'condition:{condition[1]}')
    )
    return keyboard


def request_phase() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for phase in list(DEFAULT_PHASES_DICT.keys())[::-1]:
        keyboard.add(
            InlineKeyboardButton(phase, callback_data=f'phase:{phase}')
        )
    return keyboard


def request_communication(contact_methods, selected_contact_methods):
    keyboard = InlineKeyboardMarkup()
    buttons_list = []

    for method in contact_methods[::-1]:
        # Получаем текущее состояние выбора специализации
        is_selected = selected_contact_methods.get(method)

        # Создаем кнопку для каждой специализации с зеленой галочкой, если выбрана
        button_text = f"✅ {method}" if is_selected else method
        button = InlineKeyboardButton(button_text, callback_data=f'method:{method}')
        buttons_list.append(button)

    for i in range(0, len(buttons_list), 2):
        keyboard.add(*buttons_list[i:i + 2])

    # Добавляем кнопку для подтверждения выбора
    confirm_button = InlineKeyboardButton("👍 Подтвердить выбор", callback_data="method:confirm")
    keyboard.add(confirm_button)

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

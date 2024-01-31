import json
import urllib.parse

from database.data import DEFAULT_SPEC_DICT, DEFAULT_CITY_DICT, DEFAULT_DRUGS_DICT, DEFAULT_METHODS_DICT, DEFAULT_SPEC
from database.config_data import BOT_FORM

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


def request_specialization() -> ReplyKeyboardMarkup:

    specializations = list(DEFAULT_SPEC_DICT.keys())  # Ваш список специализаций

    serialized_data = json.dumps(specializations)
    encoded_data = urllib.parse.quote(serialized_data)

    web_app_url = f"{BOT_FORM}?data={encoded_data}"

    # Создаем обычную клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Создаем кнопку для открытия веб-приложения
    button = KeyboardButton("Выбрать специализации", web_app=WebAppInfo(url=web_app_url))

    # Добавляем кнопку в клавиатуру
    keyboard.add(button)

    return keyboard


def request_city() -> ReplyKeyboardMarkup:
    specializations = list(DEFAULT_CITY_DICT.keys())  # Ваш список специализаций
    serialized_data = json.dumps(specializations)
    encoded_data = urllib.parse.quote(serialized_data)

    web_app_url = f"{BOT_FORM}?data={encoded_data}"

    # Создаем обычную клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Создаем кнопку для открытия веб-приложения
    button = KeyboardButton("Выбрать город", web_app=WebAppInfo(url=web_app_url))

    # Добавляем кнопку в клавиатуру
    keyboard.add(button)

    return keyboard


def request_telegram() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Поделиться профилем', request_contact=True))
    return keyboard


def request_area() -> ReplyKeyboardMarkup:
    specializations = list(DEFAULT_SPEC_DICT.keys())  # Ваш список специализаций
    serialized_data = json.dumps(specializations)
    encoded_data = urllib.parse.quote(serialized_data)

    web_app_url = f"{BOT_FORM}?data={encoded_data}"

    # Создаем обычную клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Создаем кнопку для открытия веб-приложения
    button = KeyboardButton("Выбрать область исследования", web_app=WebAppInfo(url=web_app_url))

    # Добавляем кнопку в клавиатуру
    keyboard.add(button)

    return keyboard


def request_drugs() -> ReplyKeyboardMarkup:
    specializations = list(DEFAULT_DRUGS_DICT.keys()) # Список препаратов
    serialized_data = json.dumps(specializations)
    encoded_data = urllib.parse.quote(serialized_data)

    web_app_url = f"{BOT_FORM}?data={encoded_data}"

    # Создаем обычную клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Создаем кнопку для открытия веб-приложения
    button = KeyboardButton("Выбрать препараты", web_app=WebAppInfo(url=web_app_url))

    # Добавляем кнопку в клавиатуру
    keyboard.add(button)

    return keyboard


def request_communication() -> ReplyKeyboardMarkup:
    communication_methods = list(DEFAULT_METHODS_DICT.keys())[::-1] # Список методов связи
    serialized_data = json.dumps(communication_methods)
    encoded_data = urllib.parse.quote(serialized_data)

    web_app_url = f"{BOT_FORM}?data={encoded_data}"

    # Создаем обычную клавиатуру
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    # Создаем кнопку для открытия веб-приложения
    button = KeyboardButton("Выбрать способы связи", web_app=WebAppInfo(url=web_app_url))

    # Добавляем кнопку в клавиатуру
    keyboard.add(button)

    return keyboard
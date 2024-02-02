import json
import time


from keyboards.reply.web_app import request_area, request_drugs, request_communication
from keyboards.inline.inline import request_condition, request_phase
from loader import bot
from states.user_states import UserInfoState
from telebot.types import Message
from telebot import types

import logging


@bot.callback_query_handler(func=lambda call: call.data.startswith('role:Врач-исследователь'), state=UserInfoState.initial)
def callback_handler(call) -> None:
    try:
        data = call.data

        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        role = data.split(':')[1]  # Получаем роль после префикса

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Вы выбрали роль: {role}")

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние role
        bot.set_state(call.from_user.id, UserInfoState.role)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['role'] = role

        bot.send_message(
            call.message.chat.id,
            "Выберите, пожалуйста, вашу терапевтическую область исследования...",
            reply_markup=request_area()
        )
    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['web_app_data'], state=UserInfoState.area)
def get_city(message: Message) -> None:
    try:
        # Пытаемся десериализовать данные из JSON
        data_ids = json.loads(message.web_app_data.data)
        if isinstance(data_ids, list):
            # Обработка полученных данных
            cities = ", ".join(data_ids)
            bot.send_message(message.chat.id, f"Выбранный город: {cities}",
                             reply_markup=types.ReplyKeyboardRemove())

            # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние city_area
            bot.set_state(message.from_user.id, UserInfoState.city_area, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['city'] = cities

            bot.send_message(message.chat.id,
                             f"Техническое сообщение - состояние пользователя: {bot.get_state(message.from_user.id)}")
            bot.send_message(message.chat.id,
                             f"Заболевание? (конкретный диагноз)")
        else:
            bot.send_message(message.chat.id, "Вы не выбрали город! Попробуйте еще раз")
    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения {message.chat.id}")
    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['text'], state=UserInfoState.city_area)
def get_contact(message: Message) -> None:
    # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние diagnosis
    bot.set_state(message.from_user.id, UserInfoState.diagnosis, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['diagnosis'] = message.text

    time.sleep(1)
    bot.send_message(message.from_user.id, f'Опишите самые важные критерии включения/невключения пациента '
                                           f'в исследование')
    time.sleep(1)
    bot.send_message(message.from_user.id, f'В том числе пол/возраст пациента.\n'
                                           f'Не вдавайтесь в подробности, не нарушайте конфиденциальность')


@bot.message_handler(content_types=['text'], state=UserInfoState.diagnosis)
def get_contact(message: Message) -> None:
    bot.send_message(message.from_user.id,
                     "Исследование проводится в условиях амбулатории/стационара?",
                     reply_markup=request_condition()
                     )
    # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние criteria
    bot.set_state(message.from_user.id, UserInfoState.criteria, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['diagnosis'] = message.text


@bot.callback_query_handler(func=lambda call: call.data.startswith('condition:'), state=UserInfoState.criteria)
def get_condition(call) -> None:
    data = call.data
    if data.startswith('condition:'):
        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        request = data.split(':')[1]

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние conditions
        bot.set_state(call.from_user.id, UserInfoState.conditions)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['condition'] = request

        bot.send_message(
            call.message.chat.id,
            "Выберите фазу исследований",
            reply_markup=request_phase()
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('phase:'), state=UserInfoState.conditions)
def get_condition(call) -> None:
    data = call.data
    if data.startswith('phase:'):
        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        request = data.split(':')[1]

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние phase
        bot.set_state(call.from_user.id, UserInfoState.phase)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['phase'] = request

        bot.send_message(
            call.message.chat.id,
            "Выберите группу препаратов из списка или введите вручную:",
            reply_markup=request_drugs()
        )


@bot.message_handler(content_types=['web_app_data', 'text'], state=UserInfoState.phase)
def get_drugs(message: Message) -> None:
    try:
        drugs = None
        if message.content_type == 'web_app_data':

            # Пытаемся десериализовать данные из JSON
            data_ids = json.loads(message.web_app_data.data)

            if isinstance(data_ids, list):

                # Обработка полученных данных
                drugs = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Выбранные препараты: {drugs}",
                                 reply_markup=types.ReplyKeyboardRemove())

            else:
                bot.send_message(message.chat.id, "Вы не выбрали препараты! Попробуйте еще раз")

        elif message.content_type == 'text':
            if len(message.text) < 4:
                # Обработка полученных данных
                drugs = message.text
                bot.send_message(message.chat.id, f"Указанные препараты: {drugs}",
                                 reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(message.chat.id, "Кажется вы отправили ошибочное название. Попробуйте еще раз")

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние drugs
        bot.set_state(message.from_user.id, UserInfoState.drugs, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['drugs'] = drugs

        bot.send_message(message.chat.id,
                         f"Для завершения процесса подбора и участия в клинических исследованиях, "
                         f"укажите предпочтительный способ связи:",
                         reply_markup=request_communication())

    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения {message.chat.id}")
    except Exception as e:
        logging.exception(e)


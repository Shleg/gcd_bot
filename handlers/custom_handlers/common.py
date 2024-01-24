import json
import re
import time

from database.config_data import COLLECTION_USERS, USER_SPEC_IDs, USER_PREF_CONTACT, USER_CONTACT_INFO
from database.data import insert_data_item_reference, \
    DEFAULT_SPEC_DICT, replace_data_item_reference, save_data_item
from database.survey_text import CITY_REFERAL_TEXT, CITY_RESEARCHER_TEXT, CONTACT_TELEGRAM_TEXT, CONTACT_WHATSAPP_TEXT, \
    CONTACT_PHONE_TEXT, CONTACT_EMAIL_TEXT, INCORRECT_EMAIL_TEXT, INCORRECT_PHONE_TEXT, \
    ROLE_REFERAL_LAST_NO_RESEARCH_TEXT, ROLE_REFERAL_LAST_RESEARCH_TEXT, LAST_TEXT, VACANCY_TEXT, RESUME_TEXT, \
    COMMUNICATION_MESSAGE

from keyboards.reply.web_app_keybord import request_telegram, request_city
from loader import bot
from states.user_states import UserInfoState
from telebot.types import Message
from telebot import types

communication_message = None


@bot.message_handler(content_types=['web_app_data'], state=UserInfoState.role)
def get_specialization(message: Message):
    try:
        # Пытаемся десериализовать данные из JSON
        data_ids = json.loads(message.web_app_data.data)
        button_text = message.web_app_data.button_text
        if isinstance(data_ids, list):
            if button_text == 'Выбрать специализации':
                # Обработка полученных данных
                specializations = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Ваши специализации: {specializations}",
                                 reply_markup=types.ReplyKeyboardRemove())

                bot.set_state(message.from_user.id, UserInfoState.specialization, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['spec'] = specializations

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_SPEC_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in data_ids]
                }
                replace_data_item_reference(request_body)

                bot.send_message(message.chat.id, CITY_REFERAL_TEXT, reply_markup=request_city())

            else:
                # Обработка полученных данных
                area = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Ваша область исследований: {area}",
                                 reply_markup=types.ReplyKeyboardRemove())

                # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние area
                bot.set_state(message.from_user.id, UserInfoState.area, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['area'] = area

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_SPEC_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in data_ids]
                }
                replace_data_item_reference(request_body)

                bot.send_message(
                    message.chat.id, CITY_RESEARCHER_TEXT, reply_markup=request_city())
        else:
            bot.send_message(message.chat.id, "Вы не выбрали специализацию! Попробуйте еще раз")
    except json.JSONDecodeError:
        bot.send_message(message.chat.id, "Ошибка при обработке данных из веб-приложения")


@bot.callback_query_handler(func=lambda call: call.data.startswith("comm"), state=[UserInfoState.clinic_research,
                                                                                   UserInfoState.no_clinic_research,
                                                                                   UserInfoState.drugs])
def get_communication(call):
    global communication_message
    data = call.data
    if data.startswith('comm:'):

        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        communication = data.split(':')[1]  # Получаем способ коммуникации
        if communication:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"Вы выбрали предпочтительный способ коммуникации: {communication}")

            # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние communication
            bot.set_state(call.from_user.id, UserInfoState.communication)
            with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                data['communication'] = communication

            # request_body = {
            #     "dataCollectionId": COLLECTION_USERS,
            #     "referringItemFieldName": USER_PREF_CONTACT,
            #     "referringItemId": data.get('id'),
            #     "newReferencedItemIds": []
            # }
            # replace_data_item_reference(request_body)

            # user_info['id] = insert_wix_data_item_tg_name('botUsers', call.from_user.username)
            # user_info['tgName] = call.from_user.username

            if communication == 'Telegram':
                communication_message = bot.send_message(
                    call.message.chat.id, CONTACT_TELEGRAM_TEXT, reply_markup=request_telegram())

            elif communication == 'WhatsApp':
                communication_message = bot.send_message(
                    call.message.chat.id, CONTACT_WHATSAPP_TEXT)

            elif communication == 'Phone':
                communication_message = bot.send_message(
                    call.message.chat.id, CONTACT_PHONE_TEXT)

            elif communication == 'Email':
                communication_message = bot.send_message(
                    call.message.chat.id, CONTACT_EMAIL_TEXT)


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.communication)
def get_contact(message: Message) -> None:
    global communication_message

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['state'] = 'last'

    if message.content_type == 'contact':

        contact_info = message.contact.phone_number
        send_contact_confirmation(message, contact_info)

    else:
        # Строка с регулярным выражением, которое соответствует символам, которые нужно удалить
        phone_pattern = r'[()\s"\'\-+_]'  # Пробелы, скобки, кавычки, дефисы, подчеркивания, плюсы и минусы
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if data.get('communication') == 'Email':
            if re.match(email_pattern, message.text):
                contact_info = message.text
                send_contact_confirmation(message, contact_info)
            else:
                text = INCORRECT_EMAIL_TEXT
                bot.send_message(message.from_user.id, text)
                if communication_message:
                    bot.send_message(message.chat.id, communication_message.text)  # Отправляем предпоследнее сообщение
        else:
            if re.sub(phone_pattern, '', message.text).isdigit():
                contact_info = message.text
                send_contact_confirmation(message, contact_info)
            else:
                text = INCORRECT_PHONE_TEXT
                bot.send_message(message.from_user.id, text)
                if communication_message:
                    bot.send_message(message.chat.id, communication_message.text)  # Отправляем предпоследнее сообщение


@bot.message_handler(content_types=['text'], state=UserInfoState.last)
def get_contact(message: Message) -> None:
    if message.text.isalpha():

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text

        if data.get('role') == 'Врач-реферал':
            if data.get('suitable_research') == 'yes':
                bot.send_message(message.from_user.id, ROLE_REFERAL_LAST_RESEARCH_TEXT.format(data["name"]))
            elif data.get('suitable_research') == 'no':
                bot.send_message(message.from_user.id,
                                 ROLE_REFERAL_LAST_NO_RESEARCH_TEXT.format(data["name"], data.get("city"),
                                                                           data.get("spec")))
        else:
            bot.send_message(message.from_user.id, LAST_TEXT.format(data["name"]))

        bot.set_state(message.from_user.id, UserInfoState.end, message.chat.id)
        time.sleep(1)
        bot.send_message(message.from_user.id, VACANCY_TEXT.format(data["name"]))
        time.sleep(1)
        bot.send_message(message.from_user.id, RESUME_TEXT)

    else:
        bot.send_message(message.from_user.id, "Имя должно состоять только из букв. Попробуйте еще раз!")


# Отдельные функции для оптимизации кода

def send_contact_confirmation(message, contact_info):
    bot.set_state(message.from_user.id, UserInfoState.last, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['contact_info'] = contact_info

    request_body = {
        "dataCollectionId": COLLECTION_USERS,
        "dataItem": {
            "data": {
                "id": data.get('id'),
                USER_CONTACT_INFO: contact_info
            }
        }
    }
    save_data_item(request_body)

    text = f"Вы указали способ связи {data.get('communication')}: {contact_info}"
    bot.send_message(message.from_user.id, text, reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.from_user.id, COMMUNICATION_MESSAGE)

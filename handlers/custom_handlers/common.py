import json
import re
import time

from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_SPEC_IDs, USER_PREF_CONTACT, USER_CONTACT_INFO, USER_NAME, \
    USER_TG_NAME, USER_CHAT_ID, USER_STATE, USER_ROLE_IDs, COLLECTION_RESEARCHES, RESEARCH_SPEC_ID
from database.data import DEFAULT_SPEC_DICT, replace_data_item_reference, save_data_item, DEFAULT_METHODS_DICT, \
    DEFAULT_ROLE_DICT, query_data_items, DEFAULT_TEMPLATE_DICT, get_bots_manager_chat_ids
from keyboards.reply.web_app import request_telegram, request_city
from loader import bot
from states.user_states import UserInfoState
import logging

communication_message = None


@bot.message_handler(content_types=['web_app_data'], state=UserInfoState.role)
def get_specialization(message: Message):
    try:
        # Пытаемся десериализовать данные из JSON
        data_ids = json.loads(message.web_app_data.data)
        button_text = message.web_app_data.button_text
        if isinstance(data_ids, list):
            if button_text == '🩺  Выбрать специализации':
                # Обработка полученных данных
                specializations = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Ваши специализации: {specializations}",
                                 parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

                bot.set_state(message.from_user.id, UserInfoState.specialization, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['spec'] = data_ids

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_SPEC_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in data_ids]
                }
                replace_data_item_reference(request_body)

                bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('CITY_REFERAL_TEXT'),
                                 parse_mode='Markdown', reply_markup=request_city())

            elif button_text == '🩺  Выбрать область исследования':
                # Обработка полученных данных
                area = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Ваша область исследований: {area}",
                                 parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

                # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние area
                bot.set_state(message.from_user.id, UserInfoState.area, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['area'] = data_ids

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_SPEC_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in data_ids]
                }
                replace_data_item_reference(request_body)

                request_body = {
                    "dataCollectionId": COLLECTION_RESEARCHES,
                    "referringItemFieldName": RESEARCH_SPEC_ID,
                    "referringItemId": data.get('research_id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in data_ids]
                }
                replace_data_item_reference(request_body)

                bot.send_message(
                    message.chat.id, DEFAULT_TEMPLATE_DICT.get('CITY_RESEARCHER_TEXT'),
                    parse_mode='Markdown', reply_markup=request_city())
        # else:
        #     bot.send_message(message.chat.id, "Вы ничего не указали! Попробуйте еще раз")
    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения {message.chat.id}")
    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['web_app_data'], state=[UserInfoState.clinic_research,
                                                            UserInfoState.no_clinic_research,
                                                            UserInfoState.drugs])
def get_communication(message: Message):
    try:
        # Пытаемся десериализовать данные из JSON
        data_ids = json.loads(message.web_app_data.data)
        button_text = message.web_app_data.button_text
        if isinstance(data_ids, list):
            if button_text == '📟  Выбрать способы связи':
                # Обработка полученных данных
                comm_methods = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Выбранные способы связи: {comm_methods}",
                                 parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

                bot.set_state(message.from_user.id, UserInfoState.communication, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['comm_methods'] = data_ids
                    data['current_method_index'] = 0
                    data['contact_info'] = []

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_PREF_CONTACT,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_METHODS_DICT.get(method) for method in data_ids]
                }
                replace_data_item_reference(request_body)

                request_method_contacts(message)
        # else:
        #     bot.send_message(message.chat.id, "Вы не указали способы связи! Попробуйте еще раз")
    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения {message.chat.id}")
    except Exception as e:
        logging.exception(e)


def request_method_contacts(message: Message):
    global communication_message
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            comm_methods = data.get('comm_methods')
            index = data.get('current_method_index', 0)

        if index < len(comm_methods):
            method = comm_methods[index]

            if method == 'Telegram':
                communication_message = bot.send_message(
                    message.chat.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_TELEGRAM_TEXT'),
                    parse_mode='Markdown', reply_markup=request_telegram())

            elif method == 'WhatsApp':
                communication_message = bot.send_message(
                    message.chat.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_WHATSAPP_TEXT'), parse_mode='Markdown', )

            elif method == 'Телефон':
                communication_message = bot.send_message(
                    message.chat.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_PHONE_TEXT'), parse_mode='Markdown', )

            elif method == 'Почта':
                communication_message = bot.send_message(
                    message.chat.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_EMAIL_TEXT'), parse_mode='Markdown', )
        else:

            bot.set_state(message.from_user.id, UserInfoState.last, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                contact_info = data.get('contact_info')

            contact_info_str = '\n'.join(contact_info)

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "dataItem": {
                    "id": data.get('id'),
                    "data": {
                        "_id": data.get('_id'),
                        USER_CONTACT_INFO: contact_info_str,
                        USER_TG_NAME: message.from_user.username,
                        USER_CHAT_ID: message.chat.id
                    }
                }
            }

            save_data_item(request_body)

            bot.send_message(message.from_user.id, DEFAULT_TEMPLATE_DICT.get('COMMUNICATION_MESSAGE'),
                             parse_mode='Markdown')
    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.communication)
def get_contact(message: Message) -> None:
    global communication_message
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            contact_info = data.get('contact_info')
            comm_methods = data.get('comm_methods')
            index = data.get('current_method_index', 0)

        if message.content_type == 'contact':
            contact_info.append(f'Telegram: {message.contact.phone_number}')
            data['current_method_index'] = index + 1
            request_method_contacts(message)

        if message.content_type == 'text':
            # Строка с регулярным выражением, которое соответствует символам, которые нужно удалить
            phone_pattern = r'[()\s"\'\-+_]'  # Пробелы, скобки, кавычки, дефисы, подчеркивания, плюсы и минусы
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

            if comm_methods[index] == 'Почта':
                if re.match(email_pattern, message.text):
                    contact_info.append(f'Почта: {message.text}')
                    data['current_method_index'] = index + 1
                    request_method_contacts(message)
                else:
                    text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_EMAIL_TEXT')
                    bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                    if communication_message:
                        bot.send_message(message.chat.id, communication_message.text)

            elif comm_methods[index] == 'WhatsApp':
                if re.sub(phone_pattern, '', message.text).isdigit():
                    contact_info.append(f'WhatsApp: {message.text}')
                    data['current_method_index'] = index + 1
                    request_method_contacts(message)
                else:
                    text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_WHATSAPP_TEXT')
                    bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                    if communication_message:
                        bot.send_message(message.chat.id, communication_message.text)

            elif comm_methods[index] == 'Телефон':
                if re.sub(phone_pattern, '', message.text).isdigit():
                    contact_info.append(f'Телефон: {message.text}')
                    data['current_method_index'] = index + 1
                    request_method_contacts(message)
                else:
                    text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_PHONE_TEXT')
                    bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                    if communication_message:
                        bot.send_message(message.chat.id,
                                         communication_message.text)  # Отправляем предпоследнее сообщение
            else:
                text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_TELEGRAM_TEXT')
                bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                if communication_message:
                    bot.send_message(message.chat.id, communication_message.text)

    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['text'], state=UserInfoState.last)
def get_bot_user_name(message: Message) -> None:
    try:
        if message.text.isalpha():

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['name'] = message.text
                contact_info = data['contact_info']

            contact_info_str = '\n'.join(contact_info)

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "dataItem": {
                    "id": data.get('id'),
                    "data": {
                        "_id": data.get('_id'),
                        USER_CONTACT_INFO: contact_info_str,
                        USER_TG_NAME: message.from_user.username,
                        USER_CHAT_ID: message.chat.id,
                        USER_NAME: data.get('name')
                    }
                }
            }

            save_data_item(request_body)
            try:
                for chat_id in get_bots_manager_chat_ids():
                    try:
                        bot.send_message(
                            chat_id, DEFAULT_TEMPLATE_DICT.get('NOTICE_TEXT').format(data.get('role'),
                                                                                     data.get('tg_name')),
                            parse_mode='Markdown')
                    except Exception as e:
                        logging.exception(e)
                        # Продолжить выполнение цикла, даже если произошло исключение
                        continue
            except Exception as e:
                logging.exception(e)

            if data.get('role') == 'Врач-реферал':
                if data.get('suitable_research') == 'yes':
                    bot.send_message(message.from_user.id,
                                     DEFAULT_TEMPLATE_DICT.get('ROLE_REFERAL_LAST_RESEARCH_TEXT').format(data["name"]),
                                     parse_mode='Markdown')
                elif data.get('suitable_research') == 'no':
                    city_str = data.get('user_dif_city') or ' ,'.join(data.get('city'))
                    spec_str = data.get('user_dif_spec') or ' ,'.join(data.get('spec'))
                    user_name = data.get('name', '')
                    text = DEFAULT_TEMPLATE_DICT.get('ROLE_REFERAL_LAST_NO_RESEARCH_TEXT').format(user_name, city_str,
                                                                                                  spec_str)
                    bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            else:
                bot.send_message(message.from_user.id, DEFAULT_TEMPLATE_DICT.get('LAST_TEXT').format(data["name"]),
                                 parse_mode='Markdown')

            bot.set_state(message.from_user.id, UserInfoState.end, message.chat.id)
            time.sleep(1)
            bot.send_message(message.from_user.id, DEFAULT_TEMPLATE_DICT.get('VACANCY_TEXT').format(data["name"]),
                             parse_mode='Markdown', )
            # time.sleep(1)
            # bot.send_message(message.from_user.id, DEFAULT_TEMPLATE_DICT.get('RESUME_TEXT'), parse_mode='Markdown',)
        else:
            bot.send_message(message.from_user.id, "Имя должно состоять только из букв. Попробуйте еще раз!")
    except Exception as e:
        logging.exception(e)

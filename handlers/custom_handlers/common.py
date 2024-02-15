import json
import logging
import re
import time

from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_SPEC_IDs, USER_PREF_CONTACT, USER_CONTACT_INFO, USER_NAME, \
    USER_TG_NAME, USER_CHAT_ID, COLLECTION_RESEARCHES, RESEARCH_SPEC_ID, USER_DIF_SPEC, \
    RESEARCH_NAME, RESEARCHES_DIF_SPEC, USER_DIF_CITY
from database.data import DEFAULT_SPEC_DICT, replace_data_item_reference, save_data_item, DEFAULT_METHODS_DICT, \
    DEFAULT_TEMPLATE_DICT, get_bots_manager_chat_ids
from keyboards.inline.inline import request_specialization, request_city, request_communication
from keyboards.reply.web_app import request_telegram
from loader import bot
from states.user_states import UserInfoState
from utils.functions import clean_selected_specs, get_specs_list_name_from_wix, \
    get_default_template_dict_from_wix, clean_selected_cities, get_cities_list_name_from_wix, clean_selected_methods, \
    get_methods_list_name_from_wix


@bot.callback_query_handler(func=lambda call: call.data.startswith('spec'), state=UserInfoState.role)
def get_specialization(call):
    try:
        # Список специализаций
        specializations = get_specs_list_name_from_wix()

        specialization = call.data.split(':')[1]

        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            message_to_remove = data['message_to_remove']
            role = data.get('role')
            if not data.get('is_selected_specializations'):
                selected_specializations = clean_selected_specs()
                data['selected_specializations'] = selected_specializations
            else:
                selected_specializations = data.get('selected_specializations', {})

        if specialization in specializations:
            # Обработка выбора/отмены выбора специализации
            selected_specializations[specialization] = not selected_specializations.get(specialization)

            data['is_selected_specializations'] = True

            # Обновите клавиатуру после изменения выбора
            data['message_to_remove'] = bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                                      message_id=call.message.message_id,
                                                                      reply_markup=request_specialization(
                                                                          specializations,
                                                                          selected_specializations))

        elif 'confirm' in specialization and any(map(bool, selected_specializations.values())):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
            # Обработка подтверждения выбора
            selected_specializations_list = [spec for spec, is_selected in selected_specializations.items() if
                                             is_selected]

            # Добавить сохранение данных из предыдущего обработчика
            if role == 'Врач-реферал':
                bot.send_message(call.message.chat.id,
                                 f"Выбранные специализации: {', '.join(selected_specializations_list)}")

                bot.set_state(call.from_user.id, UserInfoState.specialization, call.message.chat.id)
                with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                    data['spec'] = selected_specializations_list[:]
                    data['user_dif_spec'] = ''

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_SPEC_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in selected_specializations_list]
                }
                replace_data_item_reference(request_body)

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "dataItem": {
                        "id": data.get('id'),
                        "data": {
                            "_id": data.get('_id'),
                            USER_TG_NAME: call.from_user.username,
                            USER_CHAT_ID: call.message.chat.id,
                            USER_DIF_SPEC: ''
                        }
                    }
                }

                save_data_item(request_body)

                bot.send_message(call.message.chat.id, get_default_template_dict_from_wix('CITY_REFERAL_TEXT'),
                                 parse_mode='Markdown',
                                 reply_markup=request_city(get_cities_list_name_from_wix(), clean_selected_cities()))


            elif role == 'Врач-исследователь':
                # Обработка полученных данных
                area = ", ".join(selected_specializations_list)
                bot.send_message(call.message.chat.id, f"Ваша область исследований: {area}",
                                 parse_mode='Markdown', reply_markup=None)

                # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние area
                bot.set_state(call.from_user.id, UserInfoState.area, call.message.chat.id)
                with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                    data['area'] = selected_specializations_list
                    data['spec'] = selected_specializations_list
                    data['user_dif_spec'] = ''

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_SPEC_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in selected_specializations_list]
                }
                replace_data_item_reference(request_body)
                # Очистили поле Специализации если оно было вручную
                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "dataItem": {
                        "id": data.get('id'),
                        "data": {
                            "_id": data.get('_id'),
                            USER_TG_NAME: call.from_user.username,
                            USER_CHAT_ID: call.message.chat.id,
                            USER_DIF_SPEC: ''
                        }
                    }
                }

                save_data_item(request_body)

                request_body = {
                    "dataCollectionId": COLLECTION_RESEARCHES,
                    "referringItemFieldName": RESEARCH_SPEC_ID,
                    "referringItemId": data.get('research_id'),
                    "newReferencedItemIds": [DEFAULT_SPEC_DICT.get(spec) for spec in selected_specializations_list]
                }
                replace_data_item_reference(request_body)

                # Очистили поле Специализации если оно было вручную
                request_research = {
                    "dataCollectionId": COLLECTION_RESEARCHES,
                    "dataItem": {
                        "id": data.get('research_id'),
                        "data": {
                            "_id": data.get('research_id'),
                            RESEARCH_NAME: 'NEW RESEARCH',
                            RESEARCHES_DIF_SPEC: ''
                        }
                    }
                }

                save_data_item(request_research)

                data['message_to_remove'] = bot.send_message(
                    call.message.chat.id, get_default_template_dict_from_wix('CITY_RESEARCHER_TEXT'),
                    parse_mode='Markdown',
                    reply_markup=request_city(get_cities_list_name_from_wix(), clean_selected_cities())
                )

            selected_specializations_list.clear()

        else:

            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
            bot.send_message(call.message.chat.id,
                             f"Вы не указали специализации!!")

            data['message_to_remove'] = bot.send_message(
                call.message.chat.id, get_default_template_dict_from_wix('SPEC_TEXT'),
                parse_mode='Markdown',
                reply_markup=request_specialization(get_specs_list_name_from_wix(), clean_selected_specs())
            )

    except Exception as e:
        logging.exception(e)


# selected_methods = clean_selected_methods()

@bot.callback_query_handler(func=lambda call: call.data.startswith('method'), state=[UserInfoState.clinic_research,
                                                                                     UserInfoState.no_clinic_research,
                                                                                     UserInfoState.drugs])
def get_communication(call):
    try:
        # global selected_methods
        # Список специализаций
        methods = get_methods_list_name_from_wix()

        method = call.data.split(':')[1]

        with bot.retrieve_data(call.from_user.id) as data:
            if not data.get('is_selected_methods'):
                selected_methods = clean_selected_methods()
                data['selected_methods'] = selected_methods
            else:
                selected_methods = data.get('selected_methods', {})

        if method in methods:
            # Обработка выбора/отмены выбора специализации
            selected_methods[method] = not selected_methods.get(method)

            data['is_selected_methods'] = True

            # Обновите клавиатуру после изменения выбора
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=request_communication(methods, selected_methods))

        elif 'confirm' in method and any(map(bool, selected_methods.values())):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)

            # Обработка подтверждения выбора
            selected_methods_list = [spec for spec, is_selected in selected_methods.items() if
                                     is_selected]

            bot.send_message(call.message.chat.id, f"Выбранные способы связи: {selected_methods_list}",
                             parse_mode='Markdown', reply_markup=None)

            bot.set_state(call.from_user.id, UserInfoState.communication)
            with bot.retrieve_data(call.from_user.id) as data:
                data['selected_methods_list'] = selected_methods_list
                data['current_method_index'] = 0
                data['contact_info'] = []

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_PREF_CONTACT,
                "referringItemId": data.get('id'),
                "newReferencedItemIds": [DEFAULT_METHODS_DICT.get(method) for method in selected_methods_list]
            }
            replace_data_item_reference(request_body)

            request_method_contacts(call)

        else:

            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
            bot.send_message(call.message.chat.id,
                             f"Вы не указали способы связи!!")

            bot.send_message(
                call.message.chat.id, get_default_template_dict_from_wix('NO_CONTACT_SELECTED'),
                parse_mode='Markdown',
                reply_markup=request_communication(get_methods_list_name_from_wix(), clean_selected_methods()))


    except Exception as e:
        logging.exception(e)


def request_method_contacts(call):
    try:
        with bot.retrieve_data(call.from_user.id) as data:
            comm_methods = data.get('selected_methods_list')
            index = data.get('current_method_index', 0)

        if index < len(comm_methods):
            method = comm_methods[index]

            if method == 'Telegram':
                data['communication_message'] = bot.send_message(
                    call.from_user.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_TELEGRAM_TEXT'),
                    parse_mode='Markdown', reply_markup=request_telegram())

            elif method == 'WhatsApp':
                data['communication_message'] = bot.send_message(
                    call.from_user.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_WHATSAPP_TEXT'), parse_mode='Markdown', )

            elif method == 'Телефон':
                data['communication_message'] = bot.send_message(
                    call.from_user.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_PHONE_TEXT'), parse_mode='Markdown', )

            elif method == 'Почта':
                data['communication_message'] = bot.send_message(
                    call.from_user.id, DEFAULT_TEMPLATE_DICT.get('CONTACT_EMAIL_TEXT'), parse_mode='Markdown', )
        else:

            bot.set_state(call.from_user.id, UserInfoState.last, )
            with bot.retrieve_data(call.from_user.id) as data:
                contact_info = data.get('contact_info', '')

            contact_info_str = '\n'.join(contact_info)

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "dataItem": {
                    "id": data.get('id'),
                    "data": {
                        "_id": data.get('_id'),
                        USER_TG_NAME: call.from_user.username,
                        USER_CHAT_ID: data.get('chat_id'),
                        USER_DIF_SPEC: data.get('user_dif_spec', ''),
                        USER_DIF_CITY: data.get('user_dif_city', ''),
                        USER_CONTACT_INFO: contact_info_str
                    }
                }
            }
            save_data_item(request_body)

            bot.send_message(call.from_user.id, DEFAULT_TEMPLATE_DICT.get('COMMUNICATION_MESSAGE'),
                             parse_mode='Markdown')
    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.communication)
def get_contact(message: Message) -> None:
    try:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            contact_info = data.get('contact_info')
            comm_methods = data.get('selected_methods_list')
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
                    if data.get('communication_message'):
                        bot.send_message(message.chat.id, data['communication_message'].text)

            elif comm_methods[index] == 'WhatsApp':
                if re.sub(phone_pattern, '', message.text).isdigit():
                    contact_info.append(f'WhatsApp: {message.text}')
                    data['current_method_index'] = index + 1
                    request_method_contacts(message)
                else:
                    text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_WHATSAPP_TEXT')
                    bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                    if data.get('communication_message'):
                        bot.send_message(message.chat.id, data['communication_message'].text)

            elif comm_methods[index] == 'Телефон':
                if re.sub(phone_pattern, '', message.text).isdigit():
                    contact_info.append(f'Телефон: {message.text}')
                    data['current_method_index'] = index + 1
                    request_method_contacts(message)
                else:
                    text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_PHONE_TEXT')
                    bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                    if data.get('communication_message'):
                        bot.send_message(message.chat.id,
                                         data['communication_message'].text)  # Отправляем предпоследнее сообщение
            else:
                text = DEFAULT_TEMPLATE_DICT.get('INCORRECT_TELEGRAM_TEXT')
                bot.send_message(message.from_user.id, text, parse_mode='Markdown', )
                if data.get('communication_message'):
                    bot.send_message(message.chat.id, data['communication_message'].text)

    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['text'], state=UserInfoState.last)
def get_bot_user_name(message: Message) -> None:
    try:
        # Проверка, что текст содержит только буквы, пробелы и, возможно, точку
        if re.match(r'^[^\d]+$', message.text, flags=re.UNICODE):
            # Удаление точки из текста
            cleaned_text = message.text.replace('.', '')

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['name'] = cleaned_text
                contact_info = data.get('contact_info', '')

            contact_info_str = '\n'.join(contact_info)

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "dataItem": {
                    "id": data.get('id'),
                    "data": {
                        "_id": data.get('_id'),
                        USER_TG_NAME: message.from_user.username,
                        USER_CHAT_ID: message.chat.id,
                        USER_DIF_SPEC: data.get('user_dif_spec', ''),
                        USER_DIF_CITY: data.get('user_dif_city', ''),
                        USER_NAME: data.get('name', ''),
                        USER_CONTACT_INFO: contact_info_str
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

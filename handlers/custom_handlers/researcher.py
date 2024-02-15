import json
import logging
import time

from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_ROLE_IDs, USER_CITY_ID, COLLECTION_RESEARCHES, RESEARCH_NAME, \
    RESEARCH_DOCTOR_ID, RESEARCH_CITY_ID, RESEARCH_DIAG_NAME, RESEARCH_CRITERIA_DESC, RESEARCH_CONDITION_IDS, \
    RESEARCH_PHASE_IDS, RESEARCHES_DRUGS, RESEARCHES_DIF_SPEC, RESEARCHES_DIF_CITY, USER_TG_NAME, USER_CHAT_ID, \
    USER_DIF_SPEC, USER_DIF_CITY, RESEARCHES_DIF_DRUGS
from database.data import DEFAULT_TEMPLATE_DICT, DEFAULT_ROLE_DICT, replace_data_item_reference, DEFAULT_CITY_DICT, \
    save_data_item, DEFAULT_CONDITION_DICT, DEFAULT_PHASES_DICT, DEFAULT_DRUGS_DICT
from keyboards.inline.inline import request_condition, request_phase, request_specialization, request_city, request_drugs
from keyboards.reply.web_app import request_communication
from loader import bot
from states.user_states import UserInfoState
from utils.functions import get_specs_list_name_from_wix, clean_selected_specs, clean_selected_cities, \
    get_cities_list_name_from_wix, get_default_template_dict_from_wix, clean_selected_drugs, \
    get_drugs_list_name_from_wix


@bot.callback_query_handler(func=lambda call: call.data.startswith('role:Врач-исследователь'),
                            state=UserInfoState.initial)
def callback_handler(call) -> None:
    try:
        message_data = call.data

        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        role = message_data.split(':')[1]  # Получаем роль после префикса

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Вы выбрали роль: {role}", parse_mode='Markdown', )

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние role
        bot.set_state(call.from_user.id, UserInfoState.role)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['role'] = role

        request_body_users = {
            "dataCollectionId": COLLECTION_USERS,
            "referringItemFieldName": USER_ROLE_IDs,
            "referringItemId": data.get('id'),
            "newReferencedItemIds": [DEFAULT_ROLE_DICT.get(role)]
        }

        replace_data_item_reference(request_body_users)

        request_body_new_research = {
            "dataCollectionId": COLLECTION_RESEARCHES,
            "dataItem": {
                "data": {
                    RESEARCH_NAME: 'NEW RESEARCH'
                }
            }
        }

        new_research = save_data_item(request_body_new_research)

        data['research_id'] = new_research['dataItem']['id']

        request_body_users = {
            "dataCollectionId": COLLECTION_RESEARCHES,
            "referringItemFieldName": RESEARCH_DOCTOR_ID,
            "referringItemId": data.get('research_id'),
            "newReferencedItemIds": [data.get('id')]
        }
        replace_data_item_reference(request_body_users)

        bot.send_message(
            call.message.chat.id, DEFAULT_TEMPLATE_DICT.get('AREA_TEXT'),
            parse_mode='Markdown',
            reply_markup=request_specialization(get_specs_list_name_from_wix(), clean_selected_specs())
        )

    except Exception as e:
        logging.exception(e)


selected_area_cities = clean_selected_cities()


@bot.callback_query_handler(func=lambda call: call.data.startswith('city'), state=UserInfoState.area)
def get_city(call) -> None:
    try:

        global selected_area_cities
        # Список городов
        cities = get_cities_list_name_from_wix()
        city = call.data.split(':')[1]

        with bot.retrieve_data(call.from_user.id) as data:
            if not data.get('selected_area_cities'):
                selected_area_cities = clean_selected_cities()

        if city in cities:
            # Обработка выбора/отмены выбора города
            selected_area_cities[city] = not selected_area_cities.get(city)

            data['selected_area_cities'] = True

            # Обновите клавиатуру после изменения выбора
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=request_city(cities, selected_area_cities))

        elif 'confirm' in city and any(map(bool, selected_area_cities.values())):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)

            # Обработка подтверждения выбора
            selected_cities_list = [city for city, is_selected in selected_area_cities.items() if is_selected]

            bot.send_message(call.from_user.id, f"Выбранный город: {', '.join(selected_cities_list)}",
                             parse_mode='Markdown')

            bot.set_state(call.from_user.id, UserInfoState.city)

            # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние city_area
            bot.set_state(call.from_user.id, UserInfoState.city_area)
            with bot.retrieve_data(call.from_user.id) as data:
                data['city'] = selected_cities_list[:]
                data['user_dif_city'] = ''

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_CITY_ID,
                "referringItemId": data.get('id'),
                "newReferencedItemIds": [DEFAULT_CITY_DICT.get(city) for city in selected_cities_list]
            }
            replace_data_item_reference(request_body)

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "referringItemFieldName": RESEARCH_CITY_ID,
                "referringItemId": data.get('research_id'),
                "newReferencedItemIds": [DEFAULT_CITY_DICT.get(city) for city in selected_cities_list]
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
                        USER_DIF_SPEC: data.get('user_dif_spec', ''),
                        USER_DIF_CITY: data.get('user_dif_city', '')
                    }
                }
            }

            save_data_item(request_body)

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "dataItem": {
                    "id": data.get('research_id'),
                    "data": {
                        "_id": data.get('research_id'),
                        RESEARCH_NAME: 'NEW RESEARCH',
                        RESEARCHES_DIF_SPEC: data.get('user_dif_spec', ''),
                        RESEARCHES_DIF_CITY: data.get('user_dif_city', '')
                    }
                }
            }

            save_data_item(request_body)

            bot.send_message(call.from_user.id,
                             DEFAULT_TEMPLATE_DICT.get('RESEARCH_DIAGNOSIS'), parse_mode='Markdown')
        else:

            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
            bot.send_message(call.message.chat.id,
                             f"Вы не указали город!!")

            bot.send_message(
                call.from_user.id, get_default_template_dict_from_wix('NO_CITY_SELECTED'),
                parse_mode='Markdown',
                reply_markup=request_city(get_cities_list_name_from_wix(), clean_selected_cities())
            )

    except Exception as e:
        logging.exception(e)


# Функция-предикат для фильтрации команд /start и /help
def not_start_help_command(message: Message):
    return not message.text.startswith('/start') and not message.text.startswith('/help')


@bot.message_handler(func=not_start_help_command, content_types=['text'], state=UserInfoState.city_area)
def get_diagnosis(message: Message) -> None:
    # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние diagnosis
    bot.set_state(message.from_user.id, UserInfoState.diagnosis, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['diagnosis_name'] = message.text

    request_body = {
        "dataCollectionId": COLLECTION_RESEARCHES,
        "dataItem": {
            "id": data.get('research_id'),
            "data": {
                "_id": data.get('research_id'),
                RESEARCH_NAME: 'NEW RESEARCH',
                RESEARCHES_DIF_SPEC: data.get('user_dif_spec', ''),
                RESEARCHES_DIF_CITY: data.get('user_dif_city', ''),
                RESEARCH_DIAG_NAME: data.get('diagnosis_name', '')
            }
        }
    }
    save_data_item(request_body)

    time.sleep(0.5)
    bot.send_message(message.from_user.id, f'Опишите самые важные критерии включения/невключения пациента '
                                           f'в исследование', parse_mode='Markdown', )
    time.sleep(0.5)
    bot.send_message(message.from_user.id, f'В том числе пол/возраст пациента.\n'
                                           f'Не вдавайтесь в подробности, не нарушайте конфиденциальность',
                     parse_mode='Markdown')


@bot.message_handler(func=not_start_help_command, content_types=['text'], state=UserInfoState.diagnosis)
def get_criteria(message: Message) -> None:
    # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние criteria
    bot.set_state(message.from_user.id, UserInfoState.criteria, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['criteria'] = message.text

    request_body = {
        "dataCollectionId": COLLECTION_RESEARCHES,
        "dataItem": {
            "id": data.get('research_id'),
            "data": {
                "_id": data.get('research_id'),
                RESEARCH_NAME: 'NEW RESEARCH',
                RESEARCHES_DIF_SPEC: data.get('user_dif_spec', ''),
                RESEARCHES_DIF_CITY: data.get('user_dif_city', ''),
                RESEARCH_DIAG_NAME: data.get('diagnosis_name', ''),
                RESEARCH_CRITERIA_DESC: data.get('criteria', ''),
            }
        }
    }

    save_data_item(request_body)

    bot.send_message(message.from_user.id,
                     DEFAULT_TEMPLATE_DICT.get('RESEARCH_CONDITION'),
                     parse_mode='Markdown', reply_markup=request_condition()
                     )


@bot.callback_query_handler(func=lambda call: call.data.startswith('condition:'), state=UserInfoState.criteria)
def get_condition(call) -> None:
    data = call.data
    if data.startswith('condition:'):
        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        condition = data.split(':')[1]

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние conditions
        bot.set_state(call.from_user.id, UserInfoState.conditions)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['condition_id'] = DEFAULT_CONDITION_DICT.get(condition)

        request_body = {
            "dataCollectionId": COLLECTION_RESEARCHES,
            "referringItemFieldName": RESEARCH_CONDITION_IDS,
            "referringItemId": data.get('research_id'),
            "newReferencedItemIds": [data['condition_id']]
        }
        replace_data_item_reference(request_body)

        bot.send_message(
            call.message.chat.id,
            DEFAULT_TEMPLATE_DICT.get('PHASE_TEXT'),
            parse_mode='Markdown', reply_markup=request_phase()
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('phase:'), state=UserInfoState.conditions)
def get_condition(call) -> None:
    data = call.data
    if data.startswith('phase:'):
        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        phase = data.split(':')[1]

        # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние phase
        bot.set_state(call.from_user.id, UserInfoState.phase)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['phase_id'] = DEFAULT_PHASES_DICT.get(phase)

        request_body = {
            "dataCollectionId": COLLECTION_RESEARCHES,
            "referringItemFieldName": RESEARCH_PHASE_IDS,
            "referringItemId": data.get('research_id'),
            "newReferencedItemIds": [data['phase_id']]
        }
        replace_data_item_reference(request_body)

        bot.send_message(
            call.from_user.id, DEFAULT_TEMPLATE_DICT.get('DRUGS_CHOICE_TEXT'),
            parse_mode='Markdown', reply_markup=request_drugs(get_drugs_list_name_from_wix(), clean_selected_drugs())
        )


selected_drugs = clean_selected_drugs()


@bot.callback_query_handler(func=lambda call: call.data.startswith('drug:'), state=UserInfoState.phase)
def get_drugs(call) -> None:
    try:
        global selected_drugs
        # Список специализаций
        drugs = get_drugs_list_name_from_wix()
        drug = call.data.split(':')[1]

        with bot.retrieve_data(call.from_user.id) as data:
            if not data.get('selected_drugs'):
                selected_drugs = clean_selected_drugs()

        if drug in drugs:
            # Обработка выбора/отмены выбора специализации
            selected_drugs[drug] = not selected_drugs.get(drug)

            data['selected_drugs'] = True

            # Обновите клавиатуру после изменения выбора
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=request_drugs(drugs, selected_drugs))

        elif 'confirm' in drug and any(map(bool, selected_drugs.values())):
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)

            # Обработка подтверждения выбора
            selected_drugs_list = [drug for drug, is_selected in selected_drugs.items() if is_selected]

            bot.send_message(call.message.chat.id, f"Выбранные препараты: {', '.join(selected_drugs_list)}",
                             parse_mode='Markdown')

            bot.set_state(call.from_user.id, UserInfoState.drugs)
            with bot.retrieve_data(call.from_user.id) as data:
                data['drugs'] = selected_drugs_list
                data['research_dif_drugs'] = ''

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "referringItemFieldName": RESEARCHES_DRUGS,
                "referringItemId": data.get('research_id'),
                "newReferencedItemIds": [DEFAULT_DRUGS_DICT.get(drug) for drug in selected_drugs_list]
            }
            replace_data_item_reference(request_body)

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "dataItem": {
                    "id": data.get('research_id'),
                    "data": {
                        "_id": data.get('research_id'),
                        RESEARCH_NAME: 'NEW RESEARCH',
                        RESEARCHES_DIF_SPEC: data.get('user_dif_spec', ''),
                        RESEARCHES_DIF_CITY: data.get('user_dif_city', ''),
                        RESEARCH_DIAG_NAME: data.get('diagnosis_name', ''),
                        RESEARCH_CRITERIA_DESC: data.get('criteria', ''),
                        RESEARCHES_DIF_DRUGS: data.get('research_dif_drugs', ''),
                    }
                }
            }

            save_data_item(request_body)

            bot.send_message(call.from_user.id,
                             DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT'),
                             parse_mode='Markdown', reply_markup=request_communication())

        else:

            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=None)
            bot.send_message(call.message.chat.id,
                             f"Вы не указали препараты!!")

            bot.send_message(
                call.message.chat.id, get_default_template_dict_from_wix('DRUGS_CHOICE_TEXT'),
                parse_mode='Markdown',
                reply_markup=request_drugs(get_drugs_list_name_from_wix(), clean_selected_drugs())
            )

    except Exception as e:
        logging.exception(e)

# @bot.message_handler(content_types='web_app_data', state=UserInfoState.phase)
# def get_drugs(message: Message) -> None:
#     try:
#         drugs = None
#         if message.content_type == 'web_app_data':
#
#             # Пытаемся десериализовать данные из JSON
#             data_ids = json.loads(message.web_app_data.data)
#
#             if isinstance(data_ids, list):
#                 # Обработка полученных данных
#                 drugs = ", ".join(data_ids)
#                 bot.send_message(message.chat.id, f"Указанные препараты: {drugs}",
#                                  parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
#                 bot.set_state(message.from_user.id, UserInfoState.drugs, message.chat.id)
#                 with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
#                     data['drugs'] = data_ids
#                     data['research_dif_drugs'] = ''
#
#                 request_body = {
#                     "dataCollectionId": COLLECTION_RESEARCHES,
#                     "referringItemFieldName": RESEARCHES_DRUGS,
#                     "referringItemId": data.get('research_id'),
#                     "newReferencedItemIds": [DEFAULT_DRUGS_DICT.get(drug) for drug in data_ids]
#                 }
#                 replace_data_item_reference(request_body)
#
#                 request_body = {
#                     "dataCollectionId": COLLECTION_RESEARCHES,
#                     "dataItem": {
#                         "id": data.get('research_id'),
#                         "data": {
#                             "_id": data.get('research_id'),
#                             RESEARCH_NAME: 'NEW RESEARCH',
#                             RESEARCHES_DIF_SPEC: data.get('user_dif_spec', ''),
#                             RESEARCHES_DIF_CITY: data.get('user_dif_city', ''),
#                             RESEARCH_DIAG_NAME: data.get('diagnosis_name', ''),
#                             RESEARCH_CRITERIA_DESC: data.get('criteria', ''),
#                             RESEARCHES_DIF_DRUGS: data.get('research_dif_drugs', ''),
#                         }
#                     }
#                 }
#
#                 save_data_item(request_body)
#
#                 bot.send_message(message.chat.id,
#                                  DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT'),
#                                  parse_mode='Markdown', reply_markup=request_communication())
#
#     except Exception as e:
#         logging.exception(e)

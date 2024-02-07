import json
import logging
import time

from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_ROLE_IDs, USER_CITY_ID, COLLECTION_RESEARCHES, RESEARCH_NAME, \
    RESEARCH_DOCTOR_ID, RESEARCH_CITY_ID, RESEARCH_DIAG_NAME, RESEARCH_CRITERIA_DESC, RESEARCH_CONDITION_IDS, \
    RESEARCH_PHASE_IDS, RESEARCHES_DRUGS, RESEARCHES_DIF_SPEC, RESEARCHES_DIF_CITY
from database.data import DEFAULT_TEMPLATE_DICT, DEFAULT_ROLE_DICT, replace_data_item_reference, DEFAULT_CITY_DICT, \
    save_data_item, DEFAULT_CONDITION_DICT, DEFAULT_PHASES_DICT, DEFAULT_DRUGS_DICT
from keyboards.inline.inline import request_condition, request_phase
from keyboards.reply.web_app import request_area, request_drugs, request_communication
from loader import bot
from states.user_states import UserInfoState


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
            parse_mode='Markdown', reply_markup=request_area()
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
                             parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

            # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние city_area
            bot.set_state(message.from_user.id, UserInfoState.city_area, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['city'] = data_ids

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_CITY_ID,
                "referringItemId": data.get('id'),
                "newReferencedItemIds": [DEFAULT_CITY_DICT.get(city) for city in data_ids]
            }
            replace_data_item_reference(request_body)

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "referringItemFieldName": RESEARCH_CITY_ID,
                "referringItemId": data.get('research_id'),
                "newReferencedItemIds": [DEFAULT_CITY_DICT.get(city) for city in data_ids]
            }
            replace_data_item_reference(request_body)

            bot.send_message(message.chat.id,
                             DEFAULT_TEMPLATE_DICT.get('RESEARCH_DIAGNOSIS'), parse_mode='Markdown')

        # else:
        #     bot.send_message(message.chat.id, "Вы не выбрали город! Попробуйте еще раз")
    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения {message.chat.id}")
    except Exception as e:
        logging.exception(e)


# Функция-предикат для фильтрации команд /start и /help
def not_start_help_command(message: Message):
    return not message.text.startswith('/start') and not message.text.startswith('/help')


@bot.message_handler(func=not_start_help_command, content_types=['text'], state=UserInfoState.city_area)
def get_contact(message: Message) -> None:
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
                RESEARCHES_DIF_SPEC: data.get('user_dif_spec'),
                RESEARCHES_DIF_CITY: data.get('user_dif_spec'),
                RESEARCH_DIAG_NAME: data.get('diagnosis_name')
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
def get_contact(message: Message) -> None:
    bot.send_message(message.from_user.id,
                     DEFAULT_TEMPLATE_DICT.get('RESEARCH_CONDITION'),
                     parse_mode='Markdown', reply_markup=request_condition()
                     )
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
                RESEARCHES_DIF_SPEC: data.get('user_dif_spec'),
                RESEARCHES_DIF_CITY: data.get('user_dif_spec'),
                RESEARCH_DIAG_NAME: data.get('diagnosis_name'),
                RESEARCH_CRITERIA_DESC: data.get('criteria'),
            }
        }
    }

    save_data_item(request_body)


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
            call.message.chat.id, DEFAULT_TEMPLATE_DICT.get('DRUGS_CHOICE_TEXT'),
            parse_mode='Markdown', reply_markup=request_drugs()
        )


@bot.message_handler(content_types='web_app_data', state=UserInfoState.phase)
def get_drugs(message: Message) -> None:
    try:
        drugs = None
        if message.content_type == 'web_app_data':

            # Пытаемся десериализовать данные из JSON
            data_ids = json.loads(message.web_app_data.data)

            if isinstance(data_ids, list):
                # Обработка полученных данных
                drugs = ", ".join(data_ids)
                bot.send_message(message.chat.id, f"Указанные препараты: {drugs}",
                                 parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
                bot.set_state(message.from_user.id, UserInfoState.drugs, message.chat.id)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['drugs'] = data_ids

                request_body = {
                    "dataCollectionId": COLLECTION_RESEARCHES,
                    "referringItemFieldName": RESEARCHES_DRUGS,
                    "referringItemId": data.get('research_id'),
                    "newReferencedItemIds": [DEFAULT_DRUGS_DICT.get(drug) for drug in data_ids]
                }
                replace_data_item_reference(request_body)

                bot.send_message(message.chat.id,
                                 DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT'),
                                 parse_mode='Markdown', reply_markup=request_communication())
            # else:
            #     bot.send_message(message.chat.id, "Вы не выбрали препараты! Попробуйте еще раз")
    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения {message.chat.id}")
    except Exception as e:
        logging.exception(e)

    # elif message.content_type == 'text':
    #     if len(message.text) > 5:
    #         # Обработка полученных данных
    #         drugs = message.text
    #         bot.send_message(message.chat.id, f"Указанные препараты: {drugs}",
    #                          reply_markup=types.ReplyKeyboardRemove())
    #
    #         # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние drugs
    #         bot.set_state(message.from_user.id, UserInfoState.drugs, message.chat.id)
    #         with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    #             data['drugs'] = drugs
    #
    # bot.send_message(message.chat.id,
    #                  f"Для завершения процесса подбора и участия в клинических исследованиях, "
    #                  f"укажите предпочтительный способ связи:",
    #                  reply_markup=request_communication())
    #     else:
    #         bot.send_message(message.chat.id, "Кажется вы отправили ошибочное название. Попробуйте еще раз",
    #                          reply_markup=types.ReplyKeyboardRemove())
    #         bot.send_message(
    #             message.chat.id,
    #             "Выберите группу препаратов из списка или введите вручную:",
    #             reply_markup=request_drugs()
    #         )

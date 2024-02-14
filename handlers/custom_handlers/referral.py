import json
import logging

from database.config_data import COLLECTION_USERS, USER_ROLE_IDs, USER_CITY_ID, USER_RESEARCH_IDs, USER_TG_NAME, \
    USER_CHAT_ID, USER_DIF_SPEC, USER_DIF_CITY
from database.data import COLLECTION_RESEARCHES_BODY, DEFAULT_ROLE_DICT, DEFAULT_CITY_DICT, replace_data_item_reference, \
    DEFAULT_TEMPLATE_DICT, save_data_item
from database.data import query_full_data_item, get_data_item

from keyboards.reply.web_app import request_communication
from keyboards.inline.inline import request_doctor_contact, request_specialization

from loader import bot
from states.user_states import UserInfoState
from telebot.types import Message
from telebot import types

from utils.functions import clean_selected_specs, get_specs_list_from_wix, get_specs_list_name_from_wix


@bot.callback_query_handler(func=lambda call: call.data.startswith('role:Врач-реферал'), state=UserInfoState.initial)
def callback_handler(call) -> None:
    try:
        data = call.data

        if data.startswith('role:'):

            # Удаление клавиатуры
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

            role = data.split(':')[1]  # Получаем роль после префикса
            if role in DEFAULT_ROLE_DICT.keys():
                # bot.answer_callback_query(call.id)
                # bot.send_message(call.message.chat.id, f"Вы выбрали роль: {role}")

                # Обновляем состояние пользователя и переходим к следующему шагу: устанавливаем состояние role
                bot.set_state(call.from_user.id, UserInfoState.role)
                with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                    data['role'] = role

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_ROLE_IDs,
                    "referringItemId": data.get('id'),
                    "newReferencedItemIds": [DEFAULT_ROLE_DICT.get(role)]
                }
                replace_data_item_reference(request_body)

                bot.send_message(
                    call.message.chat.id, DEFAULT_TEMPLATE_DICT.get('SPEC_TEXT'),
                    parse_mode='Markdown', reply_markup=request_specialization(get_specs_list_name_from_wix(), clean_selected_specs())
                )
    except Exception as e:
        logging.exception(e)


@bot.message_handler(content_types=['web_app_data'], state=UserInfoState.specialization)
def get_city(message: Message) -> None:
    try:
        # Пытаемся десериализовать данные из JSON
        data_ids = json.loads(message.web_app_data.data)
        if isinstance(data_ids, list):
            # Обработка полученных данных
            cities = ", ".join(data_ids)
            bot.send_message(message.chat.id, f"Выбранный город: {cities}",
                             parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

            bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['city'] = data_ids
                data['user_dif_city'] = ''

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_CITY_ID,
                "referringItemId": data.get('id'),
                "newReferencedItemIds": [DEFAULT_CITY_DICT.get(city) for city in data_ids]
            }
            replace_data_item_reference(request_body)

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
                    }
                }
            }

            save_data_item(request_body)

            bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('SELECTING_TEXT'), parse_mode='Markdown')

            # Устанавливаем новое состояние пользователя
            bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)

            # Вызываем следующий обработчик вручную
            select_researches(message)

        # else:
        #     bot.send_message(message.chat.id, "Вы не выбрали город! Попробуйте еще раз")
    except json.JSONDecodeError:
        logging.error(f"Ошибка при обработке данных из веб-приложения, чат-ИД {message.chat.id}")
    except Exception as e:
        logging.exception(e)


def select_researches(message: Message):
    try:
        suitable_researches = []

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            cities = data.get('city') or data.get('user_dif_city')
            specs = data.get('spec') or data.get('user_dif_spec')

        research_list = query_full_data_item(COLLECTION_RESEARCHES_BODY)
        research_city = list()
        research_spec = list()
        for research in research_list['dataItems']:

            if research['data']['citiyId'] and research['data']['specializationsId']:
                research_city = [city.get('cityName', None) for city in research['data']['citiyId'] if city]
                research_spec = [spec.get('specializationName', None) for spec in research['data']['specializationsId']
                                 if spec]
                if data.get('id') != research['data']['researcherDoctorId'][0]['_id']:
                    if set(research_city) & set(cities) and set(research_spec) & set(specs):
                        suitable_researches.append(research)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['suitable_researches'] = suitable_researches
            data['current_research_index'] = 0

        if suitable_researches:

            bot.set_state(message.from_user.id, UserInfoState.clinic_research, message.chat.id)

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['state'] = 'clinic_research'
                data['suitable_research'] = 'yes'

            send_next_research(message)

        else:
            bot.set_state(message.from_user.id, UserInfoState.no_clinic_research, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['state'] = 'no_clinic_research'
                data['suitable_research'] = 'no'

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_RESEARCH_IDs,
                "referringItemId": data.get('id'),
                "newReferencedItemIds": []
            }

            replace_data_item_reference(request_body)

            city_str = data.get('user_dif_city') or ' ,'.join(data.get('city'))
            spec_str = data.get('user_dif_spec') or ' ,'.join(data.get('spec'))
            bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('NO_SELECTED_TEXT').format(city_str, spec_str),
                             parse_mode='Markdown', reply_markup=request_communication())
    except Exception as e:
        logging.exception(e)


def send_next_research(message: Message):
    try:
        with bot.retrieve_data(message.chat.id) as data:
            suitable_researches = data.get('suitable_researches', [])
            index = data.get('current_research_index', 0)
            state = data.get('state')
            data['checking_research'] = None

        if index < len(suitable_researches):
            suitable_research = suitable_researches[index]
            data['suitable_research_name'] = suitable_research['data']['clinicalStudiesName']
            suitable_research_name = suitable_research['data']['clinicalStudiesName']
            data['checking_research'] = suitable_research
            doctor_id = f"{suitable_research['data']['researcherDoctorId'][0]['_id']}"
            bot.send_message(message.chat.id,
                             DEFAULT_TEMPLATE_DICT.get('IS_SELECTED_TEXT').format(suitable_research_name),
                             parse_mode='Markdown', reply_markup=request_doctor_contact(doctor_id))
            data['current_research_index'] = index + 1

        else:
            if state == 'no_clinic_research':
                # city_str = ' ,'.join(data.get('city'))
                # spec_str = ' ,'.join(data.get('spec'))
                # text = DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT_NO_RESEARCH').format(city_str, spec_str)
                text = DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT_NO_RESEARCH')

                bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=request_communication())
            else:

                checked_researches = data.get('checked_researches', [])
                if not data.get('research_writed', False):
                    request_body = {
                        "dataCollectionId": COLLECTION_USERS,
                        "referringItemFieldName": USER_RESEARCH_IDs,
                        "referringItemId": data.get('id'),
                        "newReferencedItemIds": [research['id'] for research in checked_researches]
                    }
                    replace_data_item_reference(request_body)

                    data['research_writed'] = True

                bot.send_message(message.chat.id,
                                 DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT').format(data.get('city'),
                                                                                                data.get('spec')),
                                 parse_mode='Markdown', reply_markup=request_communication())

    except Exception as e:
        logging.exception(e)


# Функция-обработчик для получения контактной информации о враче
@bot.callback_query_handler(func=lambda call: call.data.startswith("cont"), state=[UserInfoState.clinic_research])
def get_doctor_contact(call):
    # Удаление клавиатуры
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    doctor = get_data_item(COLLECTION_USERS, call.data.split(':')[1])

    with bot.retrieve_data(call.message.chat.id) as data:
        suitable_research_name = data.get('suitable_research_name')
        checking_research = data.get('checking_research')
        checked_researches = []

    if doctor:
        doctor_name = f"{doctor['dataItem']['data']['doctorName']}"
        doctor_contact = f"{doctor['dataItem']['data']['contactInfo']}"

        contact_info_message = f"Исследование: {suitable_research_name}\nИмя врача: {doctor_name}\nКонтактные данные: {doctor_contact}"
        checked_researches.append(checking_research)
        data['checked_researches'] = checked_researches
        bot.send_message(call.message.chat.id, contact_info_message, parse_mode='Markdown')


    else:
        bot.send_message(call.message.chat.id, "Информация о враче не найдена.")

    send_next_research(call.message)

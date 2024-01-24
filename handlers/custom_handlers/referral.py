import json
import time

from database.config_data import COLLECTION_USERS, USER_ROLE_IDs, USER_CITY_ID, USER_RESEARCH_IDs
from database.data import DEFAULT_ROLE, COLLECTION_RESEARCHES_BODY, DEFAULT_ROLE_DICT, DEFAULT_CITIES_LIST, \
    DEFAULT_CITY_DICT, DEFAULT_RESEARCH_DICT, replace_data_item_reference
from database.data import query_full_data_item, insert_data_item_reference, get_data_item
from database.survey_text import (SPEC_TEXT, SELECTING_TEXT, NO_SELECTED_TEXT, IS_SELECTED_TEXT,
                                  REQUEST_COMMUNICATION_TEXT)

from keyboards.reply.web_app_keybord import request_specialization
from keyboards.inline.role import request_doctor_contact, request_communication

from loader import bot
from states.user_states import UserInfoState
from telebot.types import Message
from telebot import types


@bot.callback_query_handler(func=lambda call: call.data.startswith('role:Врач-реферал'), state=None)
def callback_handler(call) -> None:
    data = call.data
    if data.startswith('role:'):

        # Удаление клавиатуры
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        role = data.split(':')[1]  # Получаем роль после префикса
        if role in DEFAULT_ROLE:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"Вы выбрали роль: {role}")

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
                call.message.chat.id, SPEC_TEXT,
                reply_markup=request_specialization()
            )


@bot.message_handler(content_types=['web_app_data'], state=UserInfoState.specialization)
def get_city(message: Message) -> None:
    try:
        # Пытаемся десериализовать данные из JSON
        data_ids = json.loads(message.web_app_data.data)
        if isinstance(data_ids, list):

            # Обработка полученных данных
            cities = ", ".join(data_ids)
            bot.send_message(message.chat.id, f"Выбранный город: {cities}",
                             reply_markup=types.ReplyKeyboardRemove())

            bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['city'] = data_ids

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_CITY_ID,
                "referringItemId": data.get('id'),
                "newReferencedItemIds": [DEFAULT_CITY_DICT.get(city) for city in data_ids]
            }
            replace_data_item_reference(request_body)

            bot.send_message(message.chat.id, SELECTING_TEXT)

            suitable_researches = []

            research_list = query_full_data_item(COLLECTION_RESEARCHES_BODY)
            for research in research_list['dataItems']:
                research_city = research['data']['citiyId']['cityName']
                research_spec = research['data']['specializationsId']['specializationName']

                if research_city in data.get('city') and research_spec in data.get('spec'):
                    # suitable_researches.append(research['data']['clinicalStudiesName'])
                    suitable_researches.append(research)

                if suitable_researches:

                    for suitable_research in suitable_researches:
                        # bot.send_message(message.chat.id, f" У нас есть клинические испытания препарата {name} "
                        #                                   f"'Инсулин для подкожного введения' для сахарного диабета"
                        #                                   f" 2 типа. Получите дополнительную информацию, перейдя "
                        #                                   f"по этой {href} [ссылке].")
                        suitable_research_name = suitable_research['data']['clinicalStudiesName']

                        # doctor_info = (f"{suitable_research['data']['researcherDoctorId']['doctorName']}:"
                        #                f"{suitable_research['data']['researcherDoctorId']['contactInfo']}")
                        doctor_id = f"{suitable_research['data']['researcherDoctorId']['_id']}"

                        bot.send_message(message.chat.id, IS_SELECTED_TEXT.format(suitable_research_name),
                                         reply_markup=request_doctor_contact(doctor_id))

                    bot.set_state(message.from_user.id, UserInfoState.clinic_research, message.chat.id)
                    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                        data['state'] = 'clinic_research'
                        data['suitable_research'] = 'yes'

                    request_body = {
                        "dataCollectionId": COLLECTION_USERS,
                        "referringItemFieldName": USER_RESEARCH_IDs,
                        "referringItemId": data.get('id'),
                        "newReferencedItemIds": [research['id'] for research in suitable_researches]
                    }
                    replace_data_item_reference(request_body)

                else:
                    bot.send_message(message.chat.id, NO_SELECTED_TEXT.format(data.get('city'), data.get('spec')),
                                     reply_markup=request_communication())

                    bot.set_state(message.from_user.id, UserInfoState.no_clinic_research, message.chat.id)
                    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                        data['state'] = 'no_clinic_research'
                        data['suitable_research'] = 'no'

        else:
            bot.send_message(message.chat.id, "Вы не выбрали город! Попробуйте еще раз")
    except json.JSONDecodeError:
        bot.send_message(message.chat.id, "Ошибка при обработке данных из веб-приложения")


# Функция-обработчик для получения контактной информации о враче
@bot.callback_query_handler(func=lambda call: call.data.startswith("cont"), state=[UserInfoState.city,
                                                                                   UserInfoState.clinic_research])
def get_doctor_contact(call):
    # Удаление клавиатуры
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    doctor = get_data_item(COLLECTION_USERS, call.data.split(':')[1])

    if doctor:
        doctor_name = f"{doctor['dataItem']['data']['doctorName']}"
        doctor_contact = f"{doctor['dataItem']['data']['contactInfo']}"

        contact_info_message = f"Имя врача: {doctor_name}\nКонтактные данные: {doctor_contact}"
        bot.send_message(call.message.chat.id, contact_info_message)

    else:
        bot.send_message(call.message.chat.id, "Информация о враче не найдена.")

    bot.send_message(call.message.chat.id, REQUEST_COMMUNICATION_TEXT,
                     reply_markup=request_communication(call.from_user.id))

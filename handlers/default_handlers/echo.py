from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_TG_NAME, USER_CHAT_ID, USER_DIF_SPEC, USER_DIF_CITY, \
    COLLECTION_RESEARCHES, RESEARCH_NAME, RESEARCHES_DIF_SPEC, RESEARCHES_DIF_CITY, RESEARCH_DIAG_NAME, \
    RESEARCH_CRITERIA_DESC, RESEARCHES_DIF_DRUGS, USER_ROLE_IDs, USER_SPEC_IDs, RESEARCH_SPEC_ID, USER_CITY_ID, \
    RESEARCH_CITY_ID, RESEARCHES_DRUGS
from database.data import DEFAULT_TEMPLATE_DICT, save_data_item, replace_data_item_reference, DEFAULT_CITY_DICT
from handlers.custom_handlers.referral import send_next_research, select_researches
from handlers.default_handlers.start import bot_start
from keyboards.inline.inline import request_role, request_phase, request_condition, request_city, request_communication
from loader import bot
from states.user_states import UserInfoState
from utils.functions import get_cities_list_name_from_wix, clean_selected_cities, get_methods_list_name_from_wix, \
    clean_selected_methods


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    state = bot.get_state(message.from_user.id, message.chat.id)
    with bot.retrieve_data(message.from_user.id) as data:
        message_to_remove = data['message_to_remove']

    if state == UserInfoState.initial.name:
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)
        bot.reply_to(
            message, "Вы не выбрали роль!")
        data['message_to_remove'] = bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('ROLE_TEXT'),
                                                     reply_markup=request_role())

    elif state == UserInfoState.role.name:
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['user_dif_spec'] = message.text

        request_body = {
            "dataCollectionId": COLLECTION_USERS,
            "dataItem": {
                "id": data.get('id'),
                "data": {
                    "_id": data.get('_id'),
                    USER_TG_NAME: message.from_user.username,
                    USER_CHAT_ID: message.chat.id,
                    USER_DIF_SPEC: data.get('user_dif_spec', '')
                }
            }
        }

        save_data_item(request_body)

        request_body = {
            "dataCollectionId": COLLECTION_USERS,
            "referringItemFieldName": USER_SPEC_IDs,
            "referringItemId": data.get('id'),
            "newReferencedItemIds": []
        }
        replace_data_item_reference(request_body)

        if data.get('role') == 'Врач-реферал':

            bot.send_message(message.chat.id, f"Ваши специализации: {message.text}",
                             parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            data['message_to_remove'] = bot.send_message(message.chat.id,
                                                         DEFAULT_TEMPLATE_DICT.get('CITY_REFERAL_TEXT'),
                                                         parse_mode='Markdown',
                                                         reply_markup=request_city(get_cities_list_name_from_wix(),
                                                                                   clean_selected_cities()))
            bot.set_state(message.from_user.id, UserInfoState.specialization, message.chat.id)

        elif data.get('role') == 'Врач-исследователь':

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "referringItemFieldName": RESEARCH_SPEC_ID,
                "referringItemId": data.get('research_id'),
                "newReferencedItemIds": []
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
                        RESEARCHES_DIF_SPEC: data.get('user_dif_spec', '')
                    }
                }
            }

            save_data_item(request_research)

            bot.send_message(message.chat.id, f"Ваша область исследований: {message.text}",
                             parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
            data['message_to_remove'] = bot.send_message(message.chat.id,
                                                         DEFAULT_TEMPLATE_DICT.get('CITY_RESEARCHER_TEXT'),
                                                         parse_mode='Markdown',
                                                         reply_markup=request_city(get_cities_list_name_from_wix(),
                                                                                   clean_selected_cities()))
            bot.set_state(message.from_user.id, UserInfoState.area, message.chat.id)

    elif state in (UserInfoState.specialization.name, UserInfoState.area.name):
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['user_dif_city'] = message.text

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

        request_body = {
            "dataCollectionId": COLLECTION_USERS,
            "referringItemFieldName": USER_CITY_ID,
            "referringItemId": data.get('id'),
            "newReferencedItemIds": []
        }
        replace_data_item_reference(request_body)

        if state == UserInfoState.area.name:
            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "dataItem": {
                    "id": data.get('research_id'),
                    "data": {
                        "_id": data.get('research_id'),
                        RESEARCH_NAME: 'NEW RESEARCH',
                        RESEARCHES_DIF_SPEC: data.get('user_dif_spec', ''),
                        RESEARCHES_DIF_CITY: data.get('user_dif_city', ''),
                    }
                }
            }

            save_data_item(request_body)

            request_body = {
                "dataCollectionId": COLLECTION_RESEARCHES,
                "referringItemFieldName": RESEARCH_CITY_ID,
                "referringItemId": data.get('research_id'),
                "newReferencedItemIds": []
            }
            replace_data_item_reference(request_body)

            bot.set_state(message.from_user.id, UserInfoState.city_area, message.chat.id)
            bot.send_message(message.chat.id, f"Выбранный город: {message.text}",
                             parse_mode='Markdown', reply_markup=None)
            bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('RESEARCH_DIAGNOSIS'), parse_mode='Markdown')
        else:

            bot.send_message(message.chat.id, f"Выбранный город: {message.text}",
                             parse_mode='Markdown', reply_markup=None)
            select_researches(message)

    elif state == UserInfoState.criteria.name:
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)
        bot.reply_to(
            message, "Вы не выбрали условия исследования!")
        data['message_to_remove'] = bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('RESEARCH_CONDITION'),
                         reply_markup=request_condition())

    elif state == UserInfoState.conditions.name:
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)
        bot.reply_to(
            message, "Вы не выбрали фазу исследования!")
        data['message_to_remove'] = bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('PHASE_TEXT'), reply_markup=request_phase())

    elif state == UserInfoState.phase.name:

        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['research_dif_drugs'] = message.text

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

        request_body = {
            "dataCollectionId": COLLECTION_RESEARCHES,
            "referringItemFieldName": RESEARCHES_DRUGS,
            "referringItemId": data.get('research_id'),
            "newReferencedItemIds": []
        }
        replace_data_item_reference(request_body)

        bot.set_state(message.from_user.id, UserInfoState.drugs, message.chat.id)
        bot.send_message(message.chat.id, f"Указанные препараты: {message.text}",
                         parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
        data['message_to_remove'] = bot.send_message(message.chat.id,
                         DEFAULT_TEMPLATE_DICT.get('REQUEST_COMMUNICATION_TEXT'),
                         parse_mode='Markdown', reply_markup=request_communication(get_methods_list_name_from_wix(), clean_selected_methods()))

    elif state == UserInfoState.drugs.name:
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)
        bot.reply_to(
            message, "Вы не указали способы связи!\nВоcпользуйтесь кнопками для выбора способов связи"
        )
        data['message_to_remove'] = bot.send_message(
            message.from_user.id, DEFAULT_TEMPLATE_DICT.get('DRUGS_CHOICE_TEXT'),
            parse_mode='Markdown', reply_markup=request_communication(get_methods_list_name_from_wix(), clean_selected_methods())
        )

    elif state == UserInfoState.communication.name:
        bot.reply_to(
            message, "Вы не указали способы связи!\nВоcпользуйтесь кнопкой ниже для выбора способов связи"
        )
    elif state == UserInfoState.end.name:
        bot.reply_to(
            message, "Вы полностью прошли опрос!\nДля перезапуска выберите команду или введите команду '/start'"
        )
    elif state in (UserInfoState.clinic_research.name, UserInfoState.no_clinic_research.name):
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message_to_remove.message_id, reply_markup=None)
        bot.reply_to(
            message, "Вы не указали способы связи!")
        send_next_research(message)

    elif state is None:
        bot_start(message)

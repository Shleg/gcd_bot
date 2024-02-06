import time

from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_CHAT_ID, USER_TG_NAME, USER_STATE, USER_ROLE_IDs
from database.data import query_data_items, get_data_item, save_data_item, query_referenced_data_items, \
    DEFAULT_TEMPLATE_DICT
from keyboards.inline.inline import request_role
from loader import bot
from states.user_states import UserInfoState


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    bot.reply_to(message, DEFAULT_TEMPLATE_DICT.get('WELCOME_TEXT_1').format(message.from_user.full_name),
                 reply_markup=types.ReplyKeyboardRemove())

    time.sleep(0.5)

    bot.send_message(message.from_user.id,
                     DEFAULT_TEMPLATE_DICT.get('WELCOME_TEXT_2').format(message.from_user.full_name))

    request_body = {
        "dataCollectionId": COLLECTION_USERS,
        "query": {
            "filter": {
                USER_CHAT_ID: {"$exists": True}
            },
            "fields": [USER_CHAT_ID]
        }
    }

    request = query_data_items(request_body)

    chat_id_list = [chat_id['data']['tgChatId'] for chat_id in request['dataItems']]
    user_id = None

    if message.chat.id in chat_id_list:
        for elem in request['dataItems']:
            if elem.get('data').get('tgChatId') == message.chat.id:
                user_id = elem.get('id')
                break

        user = get_data_item(COLLECTION_USERS, user_id)

        if user:
            bot.set_state(message.from_user.id, UserInfoState.initial)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['id'] = user['dataItem']['id']
                data['_id'] = user['dataItem']['data']['_id']
                data['name'] = user['dataItem']['data'].get('doctorName')
                data['tg_name'] = user['dataItem']['data']['tgName']
                data['chat_id'] = user['dataItem']['data']['tgChatId']
                # data['state'] = user['dataItem']['data'].get('newField')

            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "referringItemFieldName": USER_ROLE_IDs,
                "referringItemId": data.get('id')
            }

            data['roles'] = [role.get('dataItem', {}).get('data', {}).get('roleName', None) for role
                             in query_referenced_data_items(request_body)['results']]

            if 'Менеджер бота' in data.get('roles'):
                bot.send_message(message.chat.id,
                                 DEFAULT_TEMPLATE_DICT.get('ADMIN_TEXT').format(message.from_user.full_name))
            else:
                bot.send_message(
                    message.chat.id, DEFAULT_TEMPLATE_DICT.get('RETURN_TEXT').format(data.get("tg_name")))
                bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('ROLE_TEXT'), reply_markup=request_role())

            # user_state = string_to_state(data['state'])
            # bot.set_state(message.from_user.id, user_state, message.chat.id)
            # process_user_state(message.from_user.id, message, user_state)

    else:

        bot.set_state(message.from_user.id, UserInfoState.initial)
        request_body = {
            "dataCollectionId": COLLECTION_USERS,
            "dataItem": {
                "data": {
                    USER_TG_NAME: message.from_user.username,
                    USER_CHAT_ID: message.chat.id,
                    # USER_STATE: bot.get_state(message.from_user.id)
                }
            }
        }
        new_user = save_data_item(request_body)
        bot.set_state(message.from_user.id, UserInfoState.initial)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['id'] = new_user['dataItem']['id']
            data['_id'] = new_user['dataItem']['data']['_id']
            data['chat_id'] = new_user['dataItem']['data']['tgChatId']
            data['tg_name'] = new_user['dataItem']['data']['tgName']
            # data['state'] = bot.get_state(message.from_user.id)

        bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('ROLE_TEXT'), reply_markup=request_role())

# Функция для преобразования строки в состояние
# def string_to_state(state_str):
#     if state_str == 'role':
#         return UserInfoState.role
#     elif state_str == 'specialization':
#         return UserInfoState.specialization
#     elif state_str == 'city':
#         return UserInfoState.city
#     elif state_str == 'clinic_research':
#         return UserInfoState.clinic_research
#     elif state_str == 'no_clinic_research':
#         return UserInfoState.no_clinic_research
#     elif state_str == 'send_request':
#         return UserInfoState.send_request
#     elif state_str == 'area':
#         return UserInfoState.area
#     elif state_str == 'city_area':
#         return UserInfoState.city_area
#     elif state_str == 'diagnosis':
#         return UserInfoState.diagnosis
#     elif state_str == 'criteria':
#         return UserInfoState.criteria
#     elif state_str == 'conditions':
#         return UserInfoState.conditions
#     elif state_str == 'phase':
#         return UserInfoState.phase
#     elif state_str == 'drugs':
#         return UserInfoState.drugs
#     elif state_str == 'communication':
#         return UserInfoState.communication
#     elif state_str == 'last':
#         return UserInfoState.last
#     else:
#         return None


# Основная функция, которая определяет, что делать на основе состояния пользователя
# def process_user_state(user_id, message, user_state):
#
#     if user_state == UserInfoState.role:
#         bot.send_message(
#             message.from_user.id,
#             "Выберите, пожалуйста, вашу специализацию...",
#             reply_markup=request_specialization()
#         )
#     elif user_state == 'specialization':
#         bot.send_message(
#             message.chat.id,
#             "Хорошо! Теперь укажите город, в котором вы ищете клиническое исследование?",
#             reply_markup=request_city()
#         )
#     elif user_state == 'city':
#         return UserInfoState.city
#     elif user_state == 'clinic_research':
#         return UserInfoState.clinic_research
#     elif user_state == 'no_clinic_research':
#         return UserInfoState.no_clinic_research
#     elif user_state == 'send_request':
#         return UserInfoState.send_request
#     elif user_state == 'area':
#         return UserInfoState.area
#     elif user_state == 'city_area':
#         return UserInfoState.city_area
#     elif user_state == 'diagnosis':
#         return UserInfoState.diagnosis
#     elif user_state == 'criteria':
#         return UserInfoState.criteria
#     elif user_state == 'conditions':
#         return UserInfoState.conditions
#     elif user_state == 'phase':
#         return UserInfoState.phase
#     elif user_state == 'drugs':
#         return UserInfoState.drugs
#     elif user_state == 'communication':
#         return UserInfoState.communication
#     elif user_state == 'last':
#         return UserInfoState.last
#     else:
#         return None

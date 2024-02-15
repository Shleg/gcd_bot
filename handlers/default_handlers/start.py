import logging
import time

from telebot import types
from telebot.types import Message

from database.config_data import COLLECTION_USERS, USER_CHAT_ID, USER_TG_NAME, USER_ROLE_IDs
from database.data import query_data_items, get_data_item, save_data_item, query_referenced_data_items, \
    DEFAULT_TEMPLATE_DICT
from keyboards.inline.inline import request_role
from loader import bot
from states.user_states import UserInfoState
from utils.functions import get_default_template_dict_from_wix


@bot.message_handler(commands=["start"])
def bot_start(message: Message):
    try:

        bot.reply_to(message, get_default_template_dict_from_wix('WELCOME_TEXT_1').format(message.from_user.full_name),
                     parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())

        time.sleep(0.5)

        bot.send_message(message.from_user.id,
                         get_default_template_dict_from_wix('WELCOME_TEXT_2').format(message.from_user.full_name),
                         parse_mode='Markdown')

        request_body = {
            "dataCollectionId": COLLECTION_USERS,
            "query": {
                "filter": {
                    USER_CHAT_ID: {"$exists": True}
                },
                "fields": [USER_CHAT_ID]
            }
        }

        # Запрашиваем информацию о пользователях в коллекции Пользователи, где заполнено поле USER_CHAT_ID
        request = None
        while request is None:
            request = query_data_items(request_body)

        # Формируем список
        chat_id_list = [chat_id['data']['tgChatId'] for chat_id in request['dataItems']]

        user_id = None
        if message.chat.id in chat_id_list:
            for elem in request['dataItems']:
                if elem.get('data').get('tgChatId') == message.chat.id:
                    user_id = elem.get('id')
                    break

            user = None
            while user is None:
                user = get_data_item(COLLECTION_USERS, user_id)

            if user:
                bot.set_state(message.from_user.id, UserInfoState.initial)
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['id'] = user['dataItem']['id']
                    data['_id'] = user['dataItem']['data']['_id']
                    data['name'] = user['dataItem']['data'].get('doctorName')
                    data['tg_name'] = user['dataItem']['data']['tgName']
                    data['chat_id'] = user['dataItem']['data']['tgChatId']
                    data['user_dif_spec'] = ''
                    data['user_dif_city'] = ''
                    data['role'] = ''
                    data['is_selected_specializations'] = False
                    data['selected_specializations'] = []
                    data['area'] = None
                    data['spec'] = None
                    data['is_selected_cities'] = False
                    data['selected_cities'] = []
                    data['is_selected_specializations'] = False
                    data['selected_specializations'] = []
                    data['is_selected_area_cities'] = False
                    data['selected_area_cities'] = []
                    data['is_selected_drugs'] = False
                    data['selected_drugs'] = []
                    data['is_selected_methods'] = False
                    data['suitable_researches'] = []
                    data['suitable_research'] = ''
                    data['checking_research'] = None
                    # очистка данный для обработчика @bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.communication)
                    data['contact_info'] = ''
                    data['selected_methods_list'] = []
                    # очистка для обработчика @bot.message_handler(content_types=['text'], state=UserInfoState.last)
                    data['name'] = ''
                    data['communication_message'] = None

                request_body = {
                    "dataCollectionId": COLLECTION_USERS,
                    "referringItemFieldName": USER_ROLE_IDs,
                    "referringItemId": data.get('id')
                }

                while not data.get('user_roles'):
                    data['user_roles'] = [role.get('dataItem', {}).get('data', {}).get('roleName', None) for role
                                          in query_referenced_data_items(request_body)['results']]

                if 'Менеджер бота' in data.get('user_roles'):
                    bot.send_message(message.chat.id,
                                     get_default_template_dict_from_wix('ADMIN_TEXT').format(
                                         message.from_user.full_name))
                else:
                    bot.send_message(
                        message.chat.id,
                        get_default_template_dict_from_wix('RETURN_TEXT').format(message.from_user.full_name),
                        parse_mode='Markdown')
                    data['message_to_remove'] = bot.send_message(message.chat.id, get_default_template_dict_from_wix('ROLE_TEXT'),
                                     parse_mode='Markdown', reply_markup=request_role())

        else:

            bot.set_state(message.from_user.id, UserInfoState.initial)
            request_body = {
                "dataCollectionId": COLLECTION_USERS,
                "dataItem": {
                    "data": {
                        USER_TG_NAME: message.from_user.username,
                        USER_CHAT_ID: message.chat.id
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
                data['user_dif_spec'] = ''
                data['user_dif_city'] = ''
                data['role'] = ''
                data['is_selected_specializations'] = False
                data['selected_specializations'] = []
                data['area'] = None
                data['spec'] = None
                data['is_selected_cities'] = False
                data['selected_cities'] = []
                data['is_selected_specializations'] = False
                data['selected_specializations'] = []
                data['is_selected_area_cities'] = False
                data['selected_area_cities'] = []
                data['is_selected_drugs'] = False
                data['selected_drugs'] = []
                data['is_selected_methods'] = False
                data['suitable_researches'] = []
                data['suitable_research'] = ''
                data['checking_research'] = None
                # очистка данный для обработчика @bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.communication)
                data['contact_info'] = ''
                data['selected_methods_list'] = []
                # очистка для обработчика @bot.message_handler(content_types=['text'], state=UserInfoState.last)
                data['name'] = ''
                data['communication_message'] = None

            data['message_to_remove'] = bot.send_message(message.chat.id, get_default_template_dict_from_wix('ROLE_TEXT'), parse_mode='Markdown',
                             reply_markup=request_role())
    except Exception as e:
        logging.exception(e)

from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    # Состояния пользователя для роли Врач-реферал
    role = State()
    specialization = State()
    city = State()
    clinic_research = State()
    no_clinic_research = State()

    # Состояния пользователя для роли Врач-исследователь
    send_request = State()
    area = State()
    city_area = State()
    diagnosis = State()
    criteria = State()
    conditions = State()
    phase = State()
    drugs = State()

    # Общие состояния для пользователей
    initial = State()
    state = State()
    communication = State()
    last = State()
    end = State()


"""
Описание полей данных bot.data

data['id'] = user['dataItem']['id']
data['_id'] = user['dataItem']['data']['_id']
data['name'] = user['dataItem']['data'].get('doctorName')
data['tg_name'] = user['dataItem']['data']['tgName']
data['chat_id'] = user['dataItem']['data']['tgChatId']
data['role'] = role
data['city'] = data_ids
"""


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
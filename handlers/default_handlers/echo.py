from typing import Any

from telebot.types import Message

from database.data import DEFAULT_TEMPLATE_DICT
from handlers.custom_handlers.referral import send_next_research
from handlers.default_handlers.start import bot_start
from keyboards.inline.inline import request_role
from states.user_states import UserInfoState
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    state = bot.get_state(message.from_user.id, message.chat.id)

    if state == UserInfoState.initial.name:
        # Удаление клавиатуры
        bot.edit_message_reply_markup(message.chat.id, message.message_id - 1, reply_markup=None)
        bot.reply_to(
            message, "Вы не выбрали роль!")
        bot.send_message(message.chat.id, DEFAULT_TEMPLATE_DICT.get('ROLE_TEXT'), reply_markup=request_role())
    elif state == UserInfoState.role.name:
        bot.reply_to(
            message, "Вы не выбрали специализацию!\nВоcпользуйтесь кнопкой ниже для выбора специализации"
        )
    elif state == UserInfoState.specialization.name:
        bot.reply_to(
            message, "Вы не выбрали город!\nВоcпользуйтесь кнопкой ниже для выбора города"
        )
    elif state == UserInfoState.city.name:
        bot.reply_to(
            message, "Вы не выбрали город!\nВоcпользуйтесь кнопкой ниже для выбора города"
        )
    elif state == UserInfoState.communication.name:
        bot.reply_to(
            message, "Вы не указали способы связи!\nВоcпользуйтесь кнопкой ниже для выбора способов связи"
        )
    elif state == UserInfoState.end.name:
        bot.reply_to(
            message, "Вы полностью прошли опрос!\nДля перезапуска выберите команду или введите команду '/start'"
        )
    elif state in (UserInfoState.clinic_research.name, UserInfoState.no_clinic_research.name, UserInfoState.drugs.name):
        send_next_research(message)
    elif state is None:
        bot_start(message)
from telebot.types import Message
from states.user_states import UserInfoState
from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    state = bot.get_state(message.from_user.id, message.chat.id)

    if state == UserInfoState.initial.name:
        bot.reply_to(
            message, "Вы не выбрали роль!\nВоcпользуйтесь кнопками выше для выбора роли"
        )
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

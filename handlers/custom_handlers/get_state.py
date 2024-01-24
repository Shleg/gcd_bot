from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=["get_state"])
def get_state(message: Message):
    bot.send_message(message.chat.id, f"Техническое сообщение - состояние пользователя: {bot.get_state(message.from_user.id)}")

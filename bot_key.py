import telebot
from telebot import types
import settings

bot = telebot.TeleBot(settings.token_telegram)  # Подключение к телеграмму


def keyboard(*args):
    """Создание клавиатуры"""
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in args:
        key.add(*[types.KeyboardButton(name) for name in [i]])
    return key

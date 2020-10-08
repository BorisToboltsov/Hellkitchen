__version__ = " $ Версия: 1.93 $ "


import threading
import time
import logic
import bot_key
from bot_key import bot


def user_id_def(message, keyboard1, keyboard):
    """Меню Действия"""
    if message.text == 'Отчет':
        bot.send_message(message.from_user.id, 'Выберите месяц или введите от 1 до 12',
                         reply_markup=bot_key.keyboard(logic.time_def()[5], logic.time_def()[6], 'Выход'))
        bot.register_next_step_handler(message, logic.month_def, keyboard)
        return
    elif message.text == 'Добавление сотрудника':
        bot.send_message(message.from_user.id, 'Введите ID телеграмм')
        bot.register_next_step_handler(message, logic.id_telegramm_def, keyboard)
    elif message.text == 'Список сотрудников':
        unit = logic.unit_salfe_def(message)
        bot.send_message(message.from_user.id, 'Выберите подразделение', reply_markup=bot_key.keyboard(unit, 'Выход'))
        bot.register_next_step_handler(message, logic.list_staff_def, keyboard)
        return
    elif message.text == 'Удаление сотрудника':
        bot.send_message(message.from_user.id, 'Введите ФИО сотрудника')
        bot.register_next_step_handler(message, logic.delete_def, keyboard)
        return
    elif message.text == 'Выход':
        bot.send_message(message.from_user.id, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    else:
        bot.reply_to(message, 'Выберете что необходимо сделать', reply_markup=keyboard1)
        bot.register_next_step_handler(message, user_id_def, keyboard1, keyboard)


def balance_month(message, keyboard):
    if message.text == 'Выход':
        bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    elif message.text == logic.time_def()[5]:
        month = logic.time_def()[0]
        threading.Thread(logic.kredit_def(message, month, keyboard))
    elif message.text == logic.time_def()[6]:
        month = logic.time_def()[4]
        threading.Thread(logic.kredit_def(message, month, keyboard))
    else:
        bot.send_message(message.from_user.id, 'Необходимо выбрать месяц, попробуйте еще раз.', reply_markup=keyboard)
        return


@bot.message_handler(func=lambda message: True, content_types=['text'])
def choice(message):
    """Основное меню"""
    key1 = 'Взять талон в столовую'
    key2 = 'Баланс'
    key3 = 'Действия'
    key4 = 'Отчет'
    key5 = 'Добавление сотрудника'
    key6 = 'Удаление сотрудника'
    key7 = 'Список сотрудников'
    key8 = 'Выход'
    keyboard1 = bot_key.keyboard(key4, key5, key6, key7, key8)
    if logic.access_def(message) is True:
        keyboard = bot_key.keyboard(key1, key2, key3)
    else:
        keyboard = bot_key.keyboard(key1, key2)
    if message.text == key1:
        threading.Thread(logic.registration(message))
    elif message.text == key2:
        bot.send_message(message.from_user.id, 'Выберите месяц',
                         reply_markup=bot_key.keyboard(logic.time_def()[5], logic.time_def()[6], 'Выход'))
        bot.register_next_step_handler(message, balance_month, keyboard)
    elif message.text == key3:
        if logic.access_def(message) is True:
            bot.send_message(message.from_user.id, 'Выберите что необходимо сделать', reply_markup=keyboard1)
            threading.Thread(bot.register_next_step_handler(message, user_id_def, keyboard1, keyboard))
        else:
            bot.send_message(message.from_user.id, 'Доступ запрещен', reply_markup=keyboard)
    elif logic.vyhod(message, keyboard) is True:
        bot.send_message(message.from_user.id, 'Выход', reply_markup=keyboard)
        return
    else:
        bot.reply_to(message, 'Нажмите на кнопку', reply_markup=keyboard)
        return


@bot.message_handler(func=lambda message: True, commands=['start'])
def start_message(message):
    if message.text == '/start':
        bot.register_next_step_handler(message, choice)


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)  # Постоянно опрашивает сервер на предмет запроса
        except Exception as e:
            # print(e)
            time.sleep(15)

import calendar
from collections import Counter
import os
import datetime
import bot_key
from bot_key import bot
import image_pillow
import sql_ps
import excel


def parse(item, state):
    """Парсинг sql ответов"""
    if state == 'string':
        a = [i[0] for i in item]
    elif state == 'string_slice':
        a = [i[0][9:11] for i in item]
    else:
        a = False
    return a


def translit_def(unit):
    """Транслитерация букв"""
    alphabet = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g',
                'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
                'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k',
                'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
                'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '',
                'ы': 'y', 'ь': "'", 'э': 'e', 'ю': 'yu',
                'я': 'ya'}
    translit = ''.join([alphabet[i] for i in unit.lower() if i in alphabet])
    return translit


def month_def(message, keyboard):
    month = message.text
    year = time_def()[1]
    last_year = int(year) - 1
    try:
        month = int(month)
        if month in range(1, 13):
            month = calendar.month_name[int(month)]
            bot.send_message(message.from_user.id, 'Выберите год',
                             reply_markup=bot_key.keyboard(last_year, int(year), 'Выход'))
            bot.register_next_step_handler(message, year_def, month, keyboard)
        else:
            bot.reply_to(message, 'Здесь необходимо ввести цифру от 1 до 12, попробуйте еще раз')
            bot.register_next_step_handler(message, month_def, keyboard)
    except ValueError:
        if message.text == 'Выход':
            bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
            return
        elif month == time_def()[5]:
            month = time_def()[0]
            bot.send_message(message.from_user.id, 'Выберите год',
                             reply_markup=bot_key.keyboard(last_year, int(year), 'Выход'))
            bot.register_next_step_handler(message, year_def, month, keyboard)
        elif month == time_def()[6]:
            month = time_def()[4]
            bot.send_message(message.from_user.id, 'Выберите год',
                             reply_markup=bot_key.keyboard(last_year, int(year), 'Выход'))
            bot.register_next_step_handler(message, year_def, month, keyboard)
        else:
            bot.reply_to(message, 'Здесь необходимо ввести цифру от 1 до 12, попробуйте еще раз')
            bot.register_next_step_handler(message, month_def, keyboard)


def year_def(message, month, keyboard):
    year = message.text
    try:
        year = int(year)
        if year in range(18, 99):
            unit = unit_salfe_def(message)
            bot.send_message(message.from_user.id, 'Выберите подразделение',
                             reply_markup=bot_key.keyboard(unit, 'Выход'))
            bot.register_next_step_handler(message, report_def, month, year, keyboard)
        else:
            bot.reply_to(message, 'Здесь необходимо ввести цифру от 18 до 99, попробуйте еще раз')
            bot.register_next_step_handler(message, year_def, month, keyboard)
    except ValueError:
        if message.text == 'Выход':
            bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
            return
        else:
            bot.reply_to(message, 'Здесь необходимо ввести последние 2 цифры года, например 20, попробуйте еще раз')
            bot.register_next_step_handler(message, year_def, month, keyboard)


def report_def(message, month, year, keyboard):
    """Отчет"""
    unit = message.text
    my_unit = unit_salfe_def(message)
    try:
        unit = unit.lower()
    except AttributeError:
        bot.reply_to(message, 'Здесь необходимо ввести подразделение')
        bot.register_next_step_handler(message, report_def, month, year, keyboard)
    if unit == '':
        bot.send_message(message.from_user.id, 'Подразделение указано неверно!', reply_markup=keyboard)
        return
    elif unit != my_unit:
        bot.send_message(message.from_user.id, 'Вы не можете смотреть отчет других подразделений',
                         reply_markup=keyboard)
        return
    unit = translit_def(unit)
    data_name = month + str(year) + unit
    records = sql_ps.all_table_list()
    answer = 'Отчета за этот период нету.'
    if data_name.lower() in records:
        sql_request = 'SELECT fio, id_telegramm FROM {}'.format(data_name)
        records = sql_ps.connect_bd(message, sql_request, 'select')
        records = Counter(records)
        list_keys = sorted(list(records.keys()))
        send_xlsx = {i[0]: records[i]*100 for i in list_keys}
        file = excel.send_xlsx(send_xlsx)
        if file is None:
            bot.send_message(message.from_user.id, 'Файл xlsx не сформирован, попробуйте еще раз.',
                             reply_markup=keyboard)
        else:
            file_open = open(file, 'rb')
            bot.send_document(message.from_user.id, file_open, reply_markup=keyboard)
            file_open.close()
            try:
                os.remove(file)
            except FileNotFoundError and PermissionError:
                print('Не прошло удаление файла!')
                pass
    else:
        bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        return


def new_staff_def(message, id_telegramm, fio, unit, keyboard):
    """Добавление нового сотрудника"""
    try:
        if message.text == 'Выход':
            bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
            return
        else:
            int(message.text)
            bot.reply_to(message, 'Необходимо ввести Да или Нет, попробуйте еще раз.')
            bot.register_next_step_handler(message, new_staff_def, id_telegramm, fio, unit, keyboard)
            return
    except ValueError:
        adm = message.text
        if adm.lower() == 'да':
            adm = 'Yes'
        elif adm.lower() == 'нет':
            adm = 'No'
        else:
            bot.reply_to(message, 'Необходимо ввести Да или Нет, попробуйте еще раз.')
            bot.register_next_step_handler(message, new_staff_def, id_telegramm, fio, unit, keyboard)
            return
        sql_request = 'SELECT id_telegramm FROM staff'
        records = sql_ps.connect_bd(message, sql_request, 'select')
        if str(id_telegramm) not in parse(records, 'string'):
            sql_request = "INSERT INTO staff(id_telegramm, fio, unit, install_date, adm) " \
                          "VALUES ('{}', '{}', '{}', '{}', '{}')".format(id_telegramm, fio, unit, time_def()[2], adm)
            sql_ps.connect_bd(message, sql_request, 'insert')
            bot.send_message(message.from_user.id, 'Сотрудник успешно добавлен', reply_markup=keyboard)
            return
        else:
            bot.send_message(message.from_user.id, 'Сотрудник с таким id уже добавлен', reply_markup=keyboard)
            return


def delete_def(message, keyboard):
    """Удаление сотрудника"""
    sql_request = 'SELECT fio FROM staff'
    records = sql_ps.connect_bd(message, sql_request, 'select')
    my_unit = unit_salfe_def(message)
    if message.text in parse(records, 'string'):
        sql_request = "SELECT unit FROM staff WHERE fio = '{}'".format(message.text)
        staff_unit = sql_ps.connect_bd(message, sql_request, 'select')
        if my_unit == staff_unit[0][0]:
            sql_request = "DELETE FROM staff WHERE fio = '{}'".format(message.text)
            sql_ps.connect_bd(message, sql_request, 'delete')
            bot.send_message(message.from_user.id, 'Сотрудник успешно удален', reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id, 'Вы не можете удалить сотрудника с другого подразделения',
                             reply_markup=keyboard)
            return
    elif message.text == 'Выход':
        bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    else:
        bot.send_message(message.from_user.id, 'Такого сотрудника нету в списке, попробуйте еще раз или нажмите "Выход"'
                         )
        bot.register_next_step_handler(message, delete_def, keyboard)
        return


def id_telegramm_def(message, keyboard):
    id_telegramm = message.text
    if id_telegramm == 'Выход':
        bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    else:
        try:
            id_telegramm = int(id_telegramm)
            bot.send_message(message.from_user.id, 'Введите ФИО сотрудника')
            bot.register_next_step_handler(message, fio_def, id_telegramm, keyboard)
        except ValueError:
            bot.send_message(message.from_user.id, 'Здесь необходимо ввести id из телеграмма, цифрами')
            bot.register_next_step_handler(message, id_telegramm_def, keyboard)
            return


def fio_def(message, id_telegramm, keyboard):
    fio = message.text
    if fio == 'Выход':
        bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    else:
        try:
            fio = int(fio)
            bot.send_message(message.from_user.id, 'Здесь необходимо ввести ФИО, буквами')
            bot.register_next_step_handler(message, fio_def, id_telegramm, keyboard)
            return
        except ValueError:
            unit = unit_salfe_def(message)
            bot.send_message(message.from_user.id, 'Выберите подразделение',
                             reply_markup=bot_key.keyboard(unit, 'Выход'))
            bot.register_next_step_handler(message, unit_def, id_telegramm, fio, keyboard)


def unit_def(message, id_telegramm, fio, keyboard):
    unit = message.text
    if unit == 'Выход':
        bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    else:
        try:
            unit = int(unit)
            bot.reply_to(message, 'Здесь необходимо ввести название подразделения на русском языке')
            bot.register_next_step_handler(message, unit_def, id_telegramm, fio, keyboard)
            return
        except ValueError:
            unit = unit.lower()
            my_unit = unit_salfe_def(message)
            sql_request = 'SELECT unit FROM staff'
            records = sql_ps.connect_bd(message, sql_request, 'select')
            if str(unit) in parse(records, 'string'):
                if unit == my_unit:
                    bot.send_message(message.from_user.id, 'Является ли сотрудник администратором?')
                    bot.register_next_step_handler(message, new_staff_def, id_telegramm, fio, unit, keyboard)
                else:
                    bot.send_message(message.from_user.id, 'Вы не можете добавить сотрудника в другое подразделение',
                                     reply_markup=keyboard)
                    return
            else:
                bot.reply_to(message, 'Такого подразделения еще не создано')
                return


def registration(message):
    """Взять талон в столовую"""
    sql_request = 'SELECT id_telegramm FROM staff'
    records = sql_ps.connect_bd(message, sql_request, 'select')
    if str(message.from_user.id) in parse(records, 'string'):
        sql_request = "SELECT unit FROM staff WHERE id_telegramm = '{}'".format(str(message.from_user.id))
        records = sql_ps.connect_bd(message, sql_request, 'select')
        unit = translit_def(records[0][0])
        if unit == '':
            bot.send_message(message.from_user.id, 'Подразделение указано неверно!')
            return
        data_name = time_def()[0]+time_def()[1]+unit
        records = sql_ps.all_table_list()
        if data_name.lower() not in records:
            sql_ps.create_new_table(data_name)
        sql_request = "SELECT install_date FROM {} WHERE id_telegramm = '{}'".format(data_name,
                                                                                     str(message.from_user.id))
        records = sql_ps.connect_bd(message, sql_request, 'select')
        if str(time_def()[3]) not in parse(records, 'string_slice'):
            sql_request = "SELECT * FROM staff WHERE id_telegramm = '{}'".format(str(message.from_user.id))
            records = sql_ps.connect_bd(message, sql_request, 'select')
            try:
                fio = records[0][2]
                sql_request = "INSERT INTO {}(id_telegramm, fio, unit, install_date, adm) " \
                              "VALUES ('{}', '{}', '{}', '{}', '{}')".format(data_name, records[0][1], records[0][2],
                                                                             records[0][3], time_def()[2], records[0][5]
                                                                             )
                sql_ps.connect_bd(message, sql_request, 'insert')
                color = 'green'
                txt = fio + "\n" + str(time_def()[2])
                image_path = image_pillow.image(txt, color)
                photo = open(image_path, 'rb')
                bot.send_photo(message.from_user.id, photo)
            except:
                bot.send_message(message.from_user.id, 'Если вы не получили талон попробуйте еще раз')
                return
            try:
                os.remove(image_path)
            except FileNotFoundError:
                return
        else:
            bot.send_message(message.from_user.id, 'Вы уже ели сегодня')
            return
    else:
        txt = 'Вы не зарегистрированы' + '\n' + 'Ваш id - ' + str(message.from_user.id)
        color = 'red'
        image_path = image_pillow.image(txt, color)
        photo = open(image_path, 'rb')
        bot.send_photo(message.from_user.id, photo)
        try:
            os.remove(image_path)
        except FileNotFoundError:
            return
    return


def time_def():
    """Даты"""
    list_month = {'January': 'Январь', 'February': 'Февраль', 'March': 'Март', 'April': 'Апрель',
                  'May': 'Май', 'June': 'Июнь', 'July': 'Июль', 'August': 'Август',
                  'September': 'Сентябрь', 'October': 'Октябрь', 'November': 'Ноябрь', 'December': 'Декабрь'}
    now = datetime.datetime.now()
    month = now.strftime('%B')
    year = now.strftime('%y')
    time = now.strftime('%H:%M:%S %d.%m.%Y')
    day = now.strftime('%d')
    month_ru = list_month[month]
    if month == 'January':
        last_month = 'December'
        last_month_ru = list_month[last_month]
    else:
        last_month = now.replace(month=int(now.month - 1))
        last_month = last_month.strftime("%B")
        last_month_ru = list_month[last_month]

    return month, year, time, day, last_month, month_ru, last_month_ru


def vyhod(*args):
    """Кнопка выход"""
    e = "Выход"
    try:
        if args[0].text.lower() == e.lower():
            bot.send_message(args[0].from_user.id, 'Выберете что необходимо сделать', reply_markup=args[1])
            return True
        else:
            return False
    except AttributeError:
        return False


def unit_salfe_def(message):
    """Определение своего подразделения"""
    sql_request = "SELECT unit FROM staff WHERE id_telegramm='{}'".format(str(message.from_user.id))
    records = sql_ps.connect_bd(message, sql_request, 'select')
    return records[0][0]


def kredit_def(message, month, keyboard):
    """Баланс"""
    sql_request = 'SELECT id_telegramm FROM staff'
    records = sql_ps.connect_bd(message, sql_request, 'select')
    if str(message.from_user.id) in parse(records, 'string'):
        sql_request = "SELECT unit FROM staff WHERE id_telegramm = '{}'".format(str(message.from_user.id))
        unit = translit_def(sql_ps.connect_bd(message, sql_request, 'select')[0][0])
        if unit == '':
            bot.send_message(message.from_user.id, 'Подразделение указано неверно!')
            return
        data_name = month + time_def()[1] + unit
        records = sql_ps.all_table_list()
        if data_name.lower() not in records:
            sql_ps.create_new_table(data_name)
        sql_request = "SELECT id_telegramm FROM {} WHERE id_telegramm = '{}'".format(data_name,
                                                                                     str(message.from_user.id))
        records = Counter(sql_ps.connect_bd(message, sql_request, 'select'))
        n = [records[i]*100 for i in records]
        try:
            answer = 'Вы должны - ' + str(n[0]) + ' рублей'
        except IndexError:
            answer = 'Вы должны 0 рублей'
        bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    else:
        txt = 'Вы не зарегистрированы' + '\n' + 'Ваш id - ' + str(message.from_user.id)
        color = 'red'
        image_path = image_pillow.image(txt, color)
        photo = open(image_path, 'rb')
        bot.send_photo(message.from_user.id, photo, reply_markup=keyboard)
        try:
            os.remove(image_path)
        except FileNotFoundError:
            return


def access_def(message):
    """Проверка на администратора"""
    user_id = str(message.from_user.id)
    sql_request = "SELECT adm FROM staff WHERE id_telegramm='{}'".format(user_id)
    records = sql_ps.connect_bd(message, sql_request, 'select')
    records = Counter(records)
    for i in records:
        if i[0] == 'Yes':
            return True
        else:
            return False


def list_staff_def(message, keyboard):
    """Список сотрудников"""
    unit = message.text
    my_unit = unit_salfe_def(message)
    if unit == 'Выход':
        bot.reply_to(message, 'Выберите что необходимо сделать', reply_markup=keyboard)
        return
    else:
        try:
            unit = int(unit)
            bot.reply_to(message, 'Здесь необходимо ввести название подразделения')
            bot.register_next_step_handler(message, list_staff_def, keyboard)
            return
        except ValueError:
            if unit == my_unit:
                unit = unit.lower()
                sql_request = "SELECT fio, adm FROM staff WHERE unit='{}'".format(unit)
                records = Counter(sql_ps.connect_bd(message, sql_request, 'select'))
                list_staff = sorted([i for i in records])
                send_xlsx = {}
                for i in list_staff:
                    send_xlsx[i[0]] = i[1]
                file = excel.send_xlsx(send_xlsx)
                if file is None:
                    bot.send_message(message.from_user.id, 'Файл xlsx не сформирован, попробуйте еще раз.',
                                     reply_markup=keyboard)
                else:
                    file_open = open(file, 'rb')
                    bot.send_document(message.from_user.id, file_open, reply_markup=keyboard)
                    file_open.close()
                    try:
                        os.remove(file)
                    except FileNotFoundError and PermissionError:
                        pass
            else:
                bot.send_message(message.from_user.id, 'Вы не можете смотреть дургое подразделение',
                                 reply_markup=keyboard)

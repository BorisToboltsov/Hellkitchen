import psycopg2
# from psycopg2 import sql
import settings
from bot_key import bot


def connect_bd(message, sql_request, state):
    """Подключение и запросы к бд"""
    try:
        conn = psycopg2.connect(dbname=settings.DB_NAME, user=settings.USER,
                                password=settings.PASSWORD, host=settings.HOST)
    except psycopg2.OperationalError:
        bot.reply_to(message, 'Не удалось подключиться к БД!')
        return
    cursor = conn.cursor()
    cursor.execute(sql_request)
    if state == 'insert':
        conn.commit()
        return
    elif state == 'delete':
        conn.commit()
        return
    elif state == 'create':
        conn.commit()
        return
    else:
        records = cursor.fetchall()
        return records

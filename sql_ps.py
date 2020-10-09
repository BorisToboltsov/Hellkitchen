import psycopg2
import settings

conn = psycopg2.connect(dbname=settings.DB_NAME, user=settings.USER, password=settings.PASSWORD, host=settings.HOST)
cursor = conn.cursor()


def connect_bd(message, sql_request, state):
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


def all_table_list():
    """Получени списка таблиц"""
    cursor.execute('''SELECT n.nspname, c.relname
                    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relkind = 'r' AND n.nspname NOT IN('pg_catalog',
                    'information_schema');''')
    records = cursor.fetchall()
    records = [i[1] for i in records]
    return records


def create_new_table(data_name):
    """Создание новой таблицы в начале месяца"""
    cursor.execute('CREATE TABLE IF NOT EXISTS {} (like staff including all)'.format(data_name))
    cursor.execute('ALTER TABLE {} DROP CONSTRAINT {}_pkey'.format(data_name, data_name))
    cursor.execute('ALTER TABLE {} ADD PRIMARY KEY (install_date)'.format(data_name))
    conn.commit()
    return

"""
def select_where(*args):
    len = len(args)
    sql_request = f'SELECT {args[0]} FROM {args[1]} WHERE {args[2]}="{args[3]}"'
    cursor.execute(sql_request)
    records = cursor.fetchall()
    return records
"""

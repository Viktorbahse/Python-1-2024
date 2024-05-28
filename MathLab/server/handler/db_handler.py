import sqlite3
import os


# Путь к файлу базы данных


def login(login, passw, signal):
    db_path = 'handler/MathLab_users.db'
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # tret="table"
    # cur.execute(f'SELECT name FROM sqlite_master WHERE type="{tret}";')
    # # Получить результат запроса
    # table_names = [table[0] for table in cur.fetchall()]
    # # Вывести имена таблиц
    # print(table_names)
    cur.execute(f'SELECT * FROM users WHERE name="{login}";')
    value = cur.fetchall()

    if value != [] and value[0][2] == passw:
        signal.emit('Успеспешная авторизация!')
    else:
        signal.emit('Проверти правильность ввода данных!')

    cur.close()
    con.close()


def register(login, passw, signal):
    db_path = 'handler/MathLab_users.db'
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE name="{login}";')
    value = cur.fetchall()

    if value!=[]:
        signal.emit('Такой ник уже есть!')
    elif value==[]:
        cur.execute(f"INSERT INTO users (name, passwor) VALUES ('{login}', '{passw}')")
        signal.emit('Успешная регистрация')
        con.commit()

    cur.close()
    con.close()

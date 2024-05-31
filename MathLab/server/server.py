from flask import Flask, request, send_from_directory, jsonify, abort
import os
import sqlite3
from pathlib import Path

db_path = 'handler/users.db'


def login(data):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE name="{data[0]}";')
    value = cur.fetchall()

    if value != [] and value[0][2] == data[1]:
        cur.execute('UPDATE users SET ssesion_id=? WHERE name=?;', (data[2], data[0]))
        con.commit()
        cur.close()
        con.close()
        return 'Успеспешная авторизация!'
    else:
        cur.close()
        con.close()
        return 'Проверти правильность ввода данных!'


def register(data):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE name="{data[0]}";')
    login = cur.fetchall()
    cur.execute(f'SELECT * FROM users WHERE email="{data[2]}";')
    email = cur.fetchall()

    if login != []:
        cur.close()
        con.close()
        return 'Извините, этот логин уже занят. Пожалуйста, выберите другой логин.'
    elif email != []:
        return 'Извините, на это почту уже зарегистрирован аккаунт.'
    elif login == [] and email == []:
        cur.execute(f"INSERT INTO users (name, password, email) VALUES ('{data[0]}', '{data[1]}', '{data[2]}')")
        con.commit()
        cur.close()
        con.close()
        Path('handler/' + data[0]).mkdir()
        con = sqlite3.connect('handler/' + data[0] + '/statistics.db')
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS levels (
                level INT PRIMARY KEY,
                completed INT DEFAULT 0
            )''')
        for i in range(1, 11):
            cur.execute("INSERT INTO levels (level) VALUES (?)", (i,))
        con.commit()
        cur.close()
        con.close()
        return 'Успешная регистрация!'


def update_statistic(login, level):
    con = sqlite3.connect('handler/' + login + '/statistics.db')
    cur = con.cursor()
    cur.execute("UPDATE levels SET completed = 1 WHERE level = " + level)
    con.commit()
    total_sum = cur.execute("SELECT SUM(completed) FROM levels").fetchone()[0]
    cur.close()
    con.close()
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('UPDATE users SET sum=? WHERE name=?;', (total_sum, login))
    con.commit()
    cur.close()
    con.close()


# Путь, где на сервере хранятся файлы
uploads_dir = os.path.join('uploads')

# Создаем её, если ей нет
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Это наш запрос. Можно в поиске http://127.0.0.1:5000/list и получить ответ
@app.route('/list', methods=['GET'])
def list_files():
    client_ip = request.remote_addr
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE ssesion_id="{client_ip}";')
    data = cur.fetchall()
    files_info = []
    if data != []:
        path = 'handler/' + str(data[0][1])
        for file_name in os.listdir(path):
            if not file_name.endswith(".db"):
                file_path = os.path.join(path, file_name)
                file_stat = os.stat(file_path)

                file_info = {
                    'name': file_name,
                    'size': file_stat.st_size,
                    'created': file_stat.st_ctime,
                    'modified': file_stat.st_mtime,  # Время последнего изменения файла
                    'accessed': file_stat.st_atime  # Время последнего доступа к файлу, это как примеры
                }
                files_info.append(file_info)


    else:
        for file_name in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, file_name)
            file_stat = os.stat(file_path)

            file_info = {
                'name': file_name,
                'size': file_stat.st_size,
                'created': file_stat.st_ctime,
                'modified': file_stat.st_mtime,  # Время последнего изменения файла
                'accessed': file_stat.st_atime  # Время последнего доступа к файлу, это как примеры
            }
            files_info.append(file_info)

    cur.close()
    con.close()
    return jsonify({'files': files_info})


# Сохранение файлов. В поиске http://127.0.0.1:5000/download/имяфайла
@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    client_ip = request.remote_addr
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE ssesion_id="{client_ip}";')
    data = cur.fetchall()
    cur.close()
    con.close()
    if data != []:
        path = 'handler/' + str(data[0][1])
        app.config['FOLDER'] = path
        filepath = os.path.join(app.config['FOLDER'], filename)
        if os.path.isfile(filepath):
            return send_from_directory(app.config['FOLDER'], filename, as_attachment=True)
        else:
            # Если файл не найден, то возвращаем ответ. Русские буквы вроде не распознает (на страничке)
            return jsonify({'error': 'File not found'})
    else:
        # Проверяем, существует ли файл
        if os.path.isfile(filepath):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            # Если файл не найден, то возвращаем ответ. Русские буквы вроде не распознает (на страничке)
            return jsonify({'error': 'File not found'})


# Загрузка на сервер. Уже на страничке не проверишь.
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']

    # Проверка наличия имени файла
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    client_ip = request.remote_addr
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE ssesion_id="{client_ip}";')
    data = cur.fetchall()
    if data != []:
        path = 'handler/' + str(data[0][1])
        app.config['FOLDER'] = path
        file.save(os.path.join(app.config['FOLDER'], file.filename))
    else:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    cur.close()
    con.close()
    return jsonify({'message': f'File {file.filename} successfully uploaded'})


@app.route('/registration', methods=['POST'])
def sign_up():
    data = request.json
    result = register(data)
    return jsonify(result)


@app.route('/login', methods=['POST'])
def log_in():
    # Получаем массив строк из запроса
    data = request.json
    client_ip = request.remote_addr
    result = login(data + [client_ip])
    return jsonify(result)


@app.route('/logout', methods=['POST'])
def logout():
    client_ip = request.remote_addr
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('UPDATE users SET ssesion_id=? WHERE ssesion_id=?;', ("null", client_ip))
    con.commit()
    cur.close()
    con.close()
    return jsonify("Ssesion_end")


@app.route('/game_statistic', methods=['POST'])
def uploading():
    level = request.json
    client_ip = request.remote_addr
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM users WHERE ssesion_id="{client_ip}";')
    data = cur.fetchall()
    message = "Вы не авторизованы!"
    if data != []:
        update_statistic(data[0][1], str(level[0]))
        message = "Статистика обнавлена."
    return jsonify(message)

@app.route('/rating', methods=['POST'])
def rating():
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT name, SUM(sum) AS total_score FROM users GROUP BY name")
    results = cur.fetchall()
    cur.close()
    con.close()
    name_sum_pairs = []
    for row in results:
        name_sum_pairs.append((row[0], row[1]))
    return jsonify(name_sum_pairs)


if __name__ == '__main__':
    app.run(debug=True)  # Чтобы был не локальный вместо этого вроде app.run(host='0.0.0.0', port=5000) нужно написать

from flask import Flask, request, send_from_directory, jsonify, abort
import os
import sqlite3


def login(data):
    db_path = 'handler/users.db'
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # tret="table"
    # cur.execute(f'SELECT name FROM sqlite_master WHERE type="{tret}";')
    # # Получить результат запроса
    # table_names = [table[0] for table in cur.fetchall()]
    # # Вывести имена таблиц
    # print(table_names)
    cur.execute(f'SELECT * FROM users WHERE name="{data[0]}";')
    value = cur.fetchall()

    if value != [] and value[0][2] == data[1]:
        cur.close()
        con.close()
        return 'Успеспешная авторизация!'
    else:
        cur.close()
        con.close()
        return 'Проверти правильность ввода данных!'


def register(data):
    db_path = 'handler/users.db'
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
        return 'Вы успешно зарегистрированы!'


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
    files_info = []

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

    return jsonify({'files': files_info})


# Сохранение файлов. В поиске http://127.0.0.1:5000/download/имяфайла
@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

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

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return jsonify({'message': f'File {file.filename} successfully uploaded'})


@app.route('/process_strings', methods=['POST'])
def process_strings():
    # Получаем массив строк из запроса
    data = request.json
    if data[0] == "login":
        result = login([data[1], data[2]])
    elif data[0] == "register":
        result = register([data[1], data[2], data[3]])
    else:
        result = "Invalid function name: " + data[0] + "!"
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)  # Чтобы был не локальный вместо этого вроде app.run(host='0.0.0.0', port=5000) нужно написать

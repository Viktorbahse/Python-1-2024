from flask import Flask, request, send_from_directory, jsonify, abort
import os

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


if __name__ == '__main__':
    app.run(debug=True)  # Чтобы был не локальный вместо этого вроде app.run(host='0.0.0.0', port=5000) нужно написать

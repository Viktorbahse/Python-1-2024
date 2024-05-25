from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QHeaderView, QFileDialog
from PyQt5.QtCore import Qt
import requests
import datetime

SERVER_URL = 'http://localhost:5000'  # И тут вроде надо изменить, чтобы не локально было


class UploadingDownloadingFiles(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server Window")
        self.setGeometry(200, 200, 800, 600)

        # Создаем таблицу
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Имя файла", "Дата создания", "Дата изменения", "Размер"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Запрещаем редактирование ячеек
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Растягиваем по ширине окна

        self.btn_upload = QPushButton("Загрузить")
        self.btn_upload.clicked.connect(self.upload_button_clicked)

        self.btn_download = QPushButton("Скачать")
        self.btn_download.clicked.connect(self.download_button_clicked)

        self.btn_list = QPushButton("Обновить список")
        self.btn_list.clicked.connect(self.update_files)

        # Создаем метку для вывода времени последнего обновления (и других сообщений)
        self.lbl_last_updated = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_upload)
        button_layout.addWidget(self.btn_download)
        button_layout.addWidget(self.btn_list)

        layout.addLayout(button_layout)
        layout.addWidget(self.lbl_last_updated)
        self.setLayout(layout)

        self.setStyleSheet("""
                    QTableWidget {
                        border: 1px solid black;
                        font-size: 14px;
                    }
                    QPushButton {
                        padding: 5px 10px;
                        font-size: 14px;
                    }
                    QLabel {
                        font-size: 12px;
                        color: (255, 255, 0, 255));
                    }
                """)

        self.update_files()

    def format_size(self, size_bytes):
        # Чтобы преобразовать размер файла в килобайты (или мегабайты)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

    def format_datetime(self, timestamp):
        # Чтобы преобразовать время
        return datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')

    def upload_file(self, filename):
        # Открываем файл, чтобы отправить на сервер
        with open(filename, 'rb') as file:
            files = {'file': file}
            response = requests.post(f'{SERVER_URL}/upload', files=files)
        return response.json()

    def download_file(self, filename):
        response = requests.get(f'{SERVER_URL}/download/{filename}')
        with open(filename, 'wb') as file:
            file.write(response.content)
        return f'File {filename} downloaded successfully'

    def list_files(self):
        response = requests.get(f'{SERVER_URL}/list')
        files = response.json()['files']
        return files

    def update_files(self):
        file_info = self.list_files()
        self.table.setRowCount(len(file_info))
        for row, file_data in enumerate(file_info):
            self.table.setItem(row, 0, QTableWidgetItem(file_data['name']))
            self.table.setItem(row, 1, QTableWidgetItem(self.format_datetime(file_data['created'])))
            self.table.setItem(row, 2, QTableWidgetItem(self.format_datetime(file_data['modified'])))
            self.table.setItem(row, 3, QTableWidgetItem(self.format_size(file_data['size'])))
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.lbl_last_updated.setText(f"Последнее обновление: {current_time}")

    def upload_button_clicked(self):
        # Открываем окно для выбора файла
        file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите файл', '', 'All files (*);;Text files (*.txt)')

        if file_path:  # Если файл выбран
            response_text = self.upload_file(file_path)
            self.lbl_last_updated.setText(response_text['message'])

    def download_button_clicked(self):
        selected_row = self.table.currentRow()  # Получаем индекс у выбранной строки

        if selected_row != -1:  # Если выбрана
            filename = self.table.item(selected_row, 0).text()
            response_text = self.download_file(filename)
            self.lbl_last_updated.setText(response_text)
        else:
            self.lbl_last_updated.setText("Выберите файл для скачивания")

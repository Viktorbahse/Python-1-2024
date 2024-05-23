from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, \
    QLabel, QHeaderView, QFileDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import QSize, Qt, QThread
from PyQt5 import QtCore
import requests
import datetime
import socket
import pickle

SERVER_URL = 'http://192.168.0.105:8080'  # И тут вроде надо изменить, чтобы не локально было


class CheckThread(QThread):
    mysignal = QtCore.pyqtSignal(str)

    # def thr_login(self, name, passw):
    #     login(name, passw, self.mysignal)
    #
    # def thr_register(self, name, passw):
    #     register(name, passw, self.mysignal)

    def thr_register(self, name, passw):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 9999))
        func_name = "register"
        strings = [name, passw]

        # Сериализация данных
        data = pickle.dumps((func_name, strings))

        # Отправка данных на сервер
        client_socket.send(data)

        # Получение результата от сервера
        result = client_socket.recv(4096)

        # Десериализация результата
        result = pickle.loads(result)

        # Закрытие соединения с сервером
        client_socket.close()
        self.mysignal.emit(result)
    def thr_login(self, name, passw):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 9999))
        func_name = "login"
        strings = [name, passw]

        # Сериализация данных
        data = pickle.dumps((func_name, strings))

        # Отправка данных на сервер
        client_socket.send(data)

        # Получение результата от сервера
        result = client_socket.recv(4096)

        # Десериализация результата
        result = pickle.loads(result)

        # Закрытие соединения с сервером
        client_socket.close()
        self.mysignal.emit(result)


class Registration_interface(QWidget):
    def __init__(self):
        super().__init__()
        self.sign_up()
        self.base_line_edit = [self.sign_up_ui.line_edit_login, self.sign_up_ui.line_edit_email,
                               self.sign_up_ui.line_edit_password]
        self.sign_up_ui.pushButton_sign_up.clicked.connect(self.reg)
        self.check_db = CheckThread()
        self.check_db.mysignal.connect(self.signal_hanler)

    def sign_up(self):
        self.setWindowTitle("Sign up")
        self.setMaximumSize(QSize(270, 160))
        self.setMinimumSize(QSize(270, 160))
        self.sign_up_ui = QWidget()
        self.sign_up_ui.verticalLayout_2 = QVBoxLayout(self)
        self.sign_up_ui.verticalLayout_2.setObjectName("verticalLayout_2")
        self.sign_up_ui.verticalLayout = QVBoxLayout()
        self.sign_up_ui.verticalLayout.setObjectName("verticalLayout")
        self.sign_up_ui.line_edit_login = QLineEdit(self)
        self.sign_up_ui.line_edit_login.setObjectName("lineEdit")
        self.sign_up_ui.verticalLayout.addWidget(self.sign_up_ui.line_edit_login)
        self.sign_up_ui.line_edit_email = QLineEdit(self)
        self.sign_up_ui.line_edit_email.setObjectName("lineEdit_2")
        self.sign_up_ui.verticalLayout.addWidget(self.sign_up_ui.line_edit_email)
        self.sign_up_ui.line_edit_password = QLineEdit(self)
        self.sign_up_ui.line_edit_password.setObjectName("lineEdit_2")
        self.sign_up_ui.verticalLayout.addWidget(self.sign_up_ui.line_edit_password)
        self.sign_up_ui.pushButton_sign_up = QPushButton(self)
        self.sign_up_ui.pushButton_sign_up.setObjectName("pushButton_sign_up")
        self.sign_up_ui.verticalLayout.addWidget(self.sign_up_ui.pushButton_sign_up)
        self.sign_up_ui.verticalLayout_2.addLayout(self.sign_up_ui.verticalLayout)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Sign up"))
        self.sign_up_ui.line_edit_login.setPlaceholderText(_translate("Form", "Login"))
        self.sign_up_ui.line_edit_email.setPlaceholderText(_translate("Form", "E-mail"))
        self.sign_up_ui.line_edit_password.setPlaceholderText(_translate("Form", "Password"))
        self.sign_up_ui.pushButton_sign_up.setText(_translate("Form", "Sign up"))
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    def reg(self):
        name = self.sign_up_ui.line_edit_login.text()
        passw = self.sign_up_ui.line_edit_password.text()
        self.check_db.thr_register(name, passw)

    def signal_hanler(self, value):
        QMessageBox.about(self, 'Оповещение', value)


class Log_in_interface(QWidget):
    def __init__(self):
        super().__init__()
        self.log_in()
        self.base_line_edit = [self.log_in_ui.line_edit_login, self.log_in_ui.line_edit_password]
        self.log_in_ui.pushButton_log_in.clicked.connect(self.auth)
        self.check_db = CheckThread()
        self.check_db.mysignal.connect(self.signal_hanler)
        # self.log_in_ui.pushButton_sign_up.clicked.connect(self.reg)

    def log_in(self):
        self.setWindowTitle("Log in or Sign up")
        self.setGeometry(650, 400, 260, 150)
        self.setMaximumSize(QSize(260, 150))
        self.setMinimumSize(QSize(260, 150))
        self.log_in_ui = QWidget()
        self.log_in_ui.verticalLayout_2 = QVBoxLayout(self)
        self.log_in_ui.verticalLayout_2.setObjectName("verticalLayout_2")
        self.log_in_ui.verticalLayout = QVBoxLayout()
        self.log_in_ui.verticalLayout.setObjectName("verticalLayout")
        self.log_in_ui.line_edit_login = QLineEdit(self)
        self.log_in_ui.line_edit_login.setObjectName("lineEdit")
        self.log_in_ui.verticalLayout.addWidget(self.log_in_ui.line_edit_login)
        self.log_in_ui.line_edit_password = QLineEdit(self)
        self.log_in_ui.line_edit_password.setObjectName("lineEdit_2")
        self.log_in_ui.verticalLayout.addWidget(self.log_in_ui.line_edit_password)
        self.log_in_ui.pushButton_log_in = QPushButton(self)
        self.log_in_ui.pushButton_log_in.setObjectName("pushButton_log_in")
        self.log_in_ui.verticalLayout.addWidget(self.log_in_ui.pushButton_log_in)
        self.log_in_ui.pushButton_sign_up = QPushButton(self)
        self.log_in_ui.pushButton_sign_up.setObjectName("pushButton_sign_up")
        self.log_in_ui.verticalLayout.addWidget(self.log_in_ui.pushButton_sign_up)
        self.log_in_ui.verticalLayout_2.addLayout(self.log_in_ui.verticalLayout)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Log in or Sign up"))
        self.log_in_ui.line_edit_login.setPlaceholderText(_translate("Form", "Login"))
        self.log_in_ui.line_edit_password.setPlaceholderText(_translate("Form", "Password"))
        self.log_in_ui.pushButton_log_in.setText(_translate("Form", "Log in"))
        self.log_in_ui.pushButton_sign_up.setText(_translate("Form", "Sign up"))
        QtCore.QMetaObject.connectSlotsByName(self)

    def check_input(funct):
        def wrapper(self):
            for line_edit in self.base_line_edit:
                if len(line_edit.text()) == 0:
                    return
            funct(self)

        return wrapper

    @check_input
    def auth(self):
        name = self.log_in_ui.line_edit_login.text()
        passw = self.log_in_ui.line_edit_password.text()
        self.check_db.thr_login(name, passw)

    def signal_hanler(self, value):
        QMessageBox.about(self, 'Оповещение', value)


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

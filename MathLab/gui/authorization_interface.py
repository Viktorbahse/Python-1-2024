from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, \
    QLabel, QHeaderView, QFileDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import QSize, Qt, QThread
from PyQt5 import QtCore
import requests

SERVER_URL = "http://127.0.0.1:5000/"  # И тут вроде надо изменить, чтобы не локально было




class ProfileButton(QPushButton):
    def __init__(self, parent, view):
        super().__init__(parent)
        self.view = view
        self.mainwindow = parent
        self.setFixedSize(55, 55)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0;
                margin-top: -10px;
                font-size: 45px;
                text-align: center;
                color: rgba(157, 161, 170, 255);
            }

            QPushButton:pressed {
                color: rgba(104, 110, 122, 255);
            }
        """)

        self.setText("😐")
        self.clicked.connect(self.open)

    def open(self):
        if self.mainwindow.is_authorized == False:
            self.mainwindow.open_authorization()
        else:
            self.mainwindow.log_out_open_widget()


class CheckThread(QThread):
    mysignal = QtCore.pyqtSignal(str)

    def thr_register(self, name, passw, email):
        data = [name, passw, email]
        result = requests.post(SERVER_URL + 'registration', json=data)
        self.mysignal.emit(result.json())

    def thr_login(self, name, passw):
        data = [name, passw]
        result = requests.post(SERVER_URL + 'login', json=data)
        result.json()
        self.mysignal.emit(result.json())


class ExitConfirmationWidget(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.setWindowTitle("Подтверждение выхода")
        self.setFixedSize(200, 100)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Вы хотите выйти?")
        self.layout.addWidget(self.label)

        self.yes_button = QPushButton("Да")
        self.yes_button.clicked.connect(self.yes_button_clicked)
        self.layout.addWidget(self.yes_button)

        self.no_button = QPushButton("Нет")
        self.no_button.clicked.connect(self.no_button_clicked)
        self.layout.addWidget(self.no_button)

    def yes_button_clicked(self):
        requests.post(SERVER_URL + 'logout')
        self.mainwindow.log_out(True)

    def no_button_clicked(self):
        self.mainwindow.log_out(False)


class Registration_interface(QWidget):
    def __init__(self, window):
        self.parent = window
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

    def check_input(funct):
        def wrapper(self):
            for line_edit in self.base_line_edit:
                if len(line_edit.text()) == 0:
                    return
            funct(self)

        return wrapper

    @check_input
    def reg(self):
        name = self.sign_up_ui.line_edit_login.text()
        passw = self.sign_up_ui.line_edit_password.text()
        email = self.sign_up_ui.line_edit_email.text()
        self.check_db.thr_register(name, passw, email)

    def signal_hanler(self, value):
        QMessageBox.about(self, 'Оповещение', value)
        if (value == 'Успешная регистрация!'):
            self.parent.successful_registration()


class Log_in_interface(QWidget):
    def __init__(self, window):
        super().__init__()
        self.parent = window
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
        if (value == 'Успеспешная авторизация!'):
            self.parent.successful_authorization()

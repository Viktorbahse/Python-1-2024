import sys
from PyQt5.QtWidgets import QApplication
from gui.mainwindow import MainWindow

full_screen_mode = True


def main():
    # Главная функция для инициализации и запуска приложения PyQt
    app = QApplication(sys.argv)
    main_window = MainWindow()  # Создание главного окна приложения.
    main_window.show()
    if full_screen_mode:
        main_window.showMaximized()
    sys.exit(app.exec_())  # Запуск основного цикла приложения и выход при его завершении.


if __name__ == '__main__':
    main()

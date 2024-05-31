import sys
from PyQt5.QtWidgets import QApplication
from gui.mainwindow import MainWindow

full_screen_mode = False


# TODO: Нашла баг с моим изменением шага сетки и изменением ширины окно. Он был и раньше, просто тут стал
#  заметнее. Пусть canvas_logical_width = 200, тогда при 400 он должен перескочить на увеличенный шаг. Но
#  изменяя размер, мы это делаем искусственно. Если установить, что можно открывать на полный экран, то видно,
#  что шаг стал многим больше, чем в изначальном маленьком окошке. Наверное, надо при изменении размера
#  инициализировать заново, но пока я не могу сказать точно


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

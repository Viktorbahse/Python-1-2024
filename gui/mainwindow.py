from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QMessageBox
from gui.canvas import Canvas
from gui.data_manager import DataManager


class MainWindow(QMainWindow):
    # Класс, представляющий главное окно
    def __init__(self):
        super().__init__()
        self.title = 'Точно не GeoGebra v0.0.0'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()  # Инициализация пользовательского интерфейса

        self.data_manager = DataManager()  # Создание экземпляра менеджера данных
        self.canvas = Canvas(self.data_manager, self)  # Создание экземпляра холста для рисования
        self.setCentralWidget(self.canvas)

    def initUI(self):
        # Метод настройки пользовательского интерфейса
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)

        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)
        self.createMenus()

        self.show()

    def createMenus(self):
        # Метод создания главного меню
        fileMenu = self.menuBar.addMenu('Файл')
        showPointsAction = QAction('Показать координаты точек', self)
        showPointsAction.triggered.connect(self.showPoints)
        fileMenu.addAction(showPointsAction)
        drawMenu = self.menuBar.addMenu('Рисование')
        # Можно добавить дополнительные действия в меню

    def showPoints(self):
        # Метод для отображения координат добавленных точек
        points = self.data_manager.get_points()  # Получение списка точек
        points_str = '\n'.join(f'Точка ({x}, {y})' for x, y in points)
        QMessageBox.information(self, "Координаты точек", points_str)  # Отображение сообщения с координатами точек
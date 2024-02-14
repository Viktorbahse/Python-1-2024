from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QMessageBox
from PyQt5.QtCore import Qt
from gui.canvas import Canvas
from gui.data_manager import DataManager
from PyQt5.QtWidgets import QAction, QActionGroup


class MainWindow(QMainWindow):
    # Класс, представляющий главное окно
    def __init__(self):
        super().__init__()
        self.title = 'Точно не GeoGebra v0.0.1'
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

        pointAction = QAction('Точки', self, checkable=True)
        lineAction = QAction('Линии', self, checkable=True)

        # Группируем действия, чтобы работали как радиокнопки
        actionGroup = QActionGroup(self)  # Используем QActionGroup для группировки
        actionGroup.addAction(pointAction)
        actionGroup.addAction(lineAction)

        # Устанавливаем действие по умолчанию (например, рисование точек)
        pointAction.setChecked(True)

        # Связываем действия с методами в классе Canvas
        pointAction.triggered.connect(lambda: self.canvas.setDrawingMode('points'))
        lineAction.triggered.connect(lambda: self.canvas.setDrawingMode('lines'))

        # Добавляем действия в меню "Рисование"
        drawMenu.addAction(pointAction)
        drawMenu.addAction(lineAction)

        # Можно добавить дополнительные действия в меню

    def showPoints(self):
        # Метод для отображения координат добавленных точек
        points = self.data_manager.get_points()  # Получение списка точек
        points_str = '\n'.join(f'Точка ({x}, {y})' for x, y in points)
        QMessageBox.information(self, "Координаты точек", points_str)  # Отображение сообщения с координатами точек

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.canvas.pan('left')
        elif event.key() == Qt.Key_Right:
            self.canvas.pan('right')
        elif event.key() == Qt.Key_Up:
            self.canvas.pan('up')
        elif event.key() == Qt.Key_Down:
            self.canvas.pan('down')

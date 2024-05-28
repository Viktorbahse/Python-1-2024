from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QVBoxLayout, QLineEdit, QAction, QLabel
from PyQt5.QtCore import Qt
from gui.custom_graphics_view import CustomGraphicsView
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, \
    QAction
from PyQt5.QtCore import Qt, QSize, QTimer
from gui.canvas import Canvas
from gui.dock_tools import DockTools
from gui.timing_widget import TimingWidget
from gui.redo_undo_buttons import *
from tests.timing import *
from gui.uploading_downloading_files import *
from core.geometric_objects.figure import *

default_size = [1200, 800]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathLab")
        self.setMinimumSize(QSize(600, 400))
        self.setGeometry(100, 100, 1200, 800)

        self.uploading_downloading_files = None
        self.display_timing = False  # Включает показ времени, за которое работает та или иная функция

        self.initUI()
        self.initMenu()

    def resizeEvent(self, event):
        new_size = event.size()  # получаем новый размер окна
        self.scene.setSceneRect(0, 0, new_size.width() - self.dockTools.width() - 2, new_size.height() - 2)
        self.view.setFixedSize(new_size.width() - self.dockTools.width(), new_size.height())
        self.scene.update_scene()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.scene = Canvas(self.width() - 200, self.height())

        self.view = CustomGraphicsView(self.scene)
        self.view.setFixedSize(1000, 800)

        self.layout.addWidget(self.view)
        self.dockTools = DockTools()

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockTools)

        self.dockTools.set_active_tool("Move")
        self.dockTools.btnAddEdFunc.clicked.connect(self.onAddEdFunc)
        self.dockTools.connect_actions(self.tool_selected)

        home_button = UndoRedoButton(parent=self, view=self.view, command="undo")
        home_button.move(260, 70)
        redo_button = UndoRedoButton(parent=self, view=self.view, command="redo")
        redo_button.move(360, 70)

        if self.display_timing:  # Текст с временем работы функции
            self.init_timing_widget()

    def initMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')
        editMenu = menubar.addMenu('Редактировать')

        serverAction = QAction('Сервер', self)
        serverAction.triggered.connect(self.open_uploading_downloading_files)  # Связываем действие с методом
        menubar.addAction(serverAction)

        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def init_timing_widget(self):
        # Создает текст, где показывается время работы функции
        self.timing_widget = TimingWidget(self)
        self.timing_widget.move(230, 45)
        self.timing_widget.resize(200, 20)
        TIMING_SIGNAL.time_updated.connect(self.timing_widget.setText)

    def open_uploading_downloading_files(self):
        if not self.uploading_downloading_files:
            self.uploading_downloading_files = UploadingDownloadingFiles()  # Создаем окно только, если оно еще не создано
        self.uploading_downloading_files.show()

    def onAddEdFunc(self):
        # self.edFuncs = {}
        self.scene.shapes_manager.functions.append(Function())
        edAndBtn = self.dockTools.addEdFunc()
        edAndBtn['ed'].textChanged.connect(self.onTextChangedEdFunc)
        edAndBtn['btn'].clicked.connect(self.onDelEdFunc)

    def findIndexEdFunc(self, wgt, indexWgt):
        cnt = self.dockTools.layEdFuncs.count()
        for i in range(cnt):
            hlay = self.dockTools.layEdFuncs.itemAt(i)
            if hlay.itemAt(indexWgt).widget() == wgt:
                return i
        return -1

    def onDelEdFunc(self):
        btn = self.sender()
        num = self.findIndexEdFunc(btn, 1)
        del self.scene.shapes_manager.functions[num]
        layItem = self.dockTools.layEdFuncs.itemAt(num)
        for i in range(layItem.count()):
            layItem.itemAt(i).widget().deleteLater()
        self.dockTools.layEdFuncs.removeItem(layItem)

    def onTextChangedEdFunc(self):
        ed = self.sender()
        num = self.findIndexEdFunc(ed, 0)
        self.scene.shapes_manager.functions[num].reset(ed.text().lower())  # Обновляем функцию.
        self.view.scene().update_scene()
        # self.scene.shapes_manager.resolve_intersections()  # Обновляем точки пересечения функций.

    def tool_selected(self, tool_name):
        self.view.current_tool = tool_name

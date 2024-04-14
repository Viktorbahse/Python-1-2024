from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QVBoxLayout, QLineEdit, QAction
from PyQt5.QtCore import Qt
from gui.custom_graphics_view import CustomGraphicsView
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QAction
from PyQt5.QtCore import Qt, QSize, QTimer
from gui.custom_graphics_view import CustomGraphicsView
from gui.canvas import Canvas
from gui.dock_tools import DockTools

default_size = [1200, 800]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathLab")
        self.setMinimumSize(QSize(600, 400))
        self.setGeometry(100, 100, 1200, 800)
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

    def initMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')
        editMenu = menubar.addMenu('Редактировать')

        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def onAddEdFunc(self):
        print("onAddEdFunc")
        # self.edFuncs = {}
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
        print(num, ": ")
        layItem = self.dockTools.layEdFuncs.itemAt(num)
        for i in range(layItem.count()):
            layItem.itemAt(i).widget().deleteLater()
        self.dockTools.layEdFuncs.removeItem(layItem)

    def onTextChangedEdFunc(self):
        ed = self.sender()
        num = self.findIndexEdFunc(ed, 0)
        print(num, ": ", ed.text())

    def tool_selected(self, tool_name):
        self.view.current_tool = tool_name

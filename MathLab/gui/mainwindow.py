from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
from MathLab.gui.custom_graphics_view import CustomGraphicsView
from MathLab.gui.canvas import Canvas
from MathLab.gui.dock_tools import DockTools


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Точно не GeoGebra")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.scene = Canvas()
        self.view = CustomGraphicsView(self.scene)
        self.view.setFixedSize(800, 600)

        self.layout.addWidget(self.view)

        self.dockTools = DockTools()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockTools)

        self.dockTools.actionModePoint.setChecked(True)

        self.dockTools.edFunc.textChanged.connect(self.testEdFunc)
        self.dockTools.actionModePoint.triggered.connect(self.setModePoint)
        self.dockTools.actionModeLine.triggered.connect(self.setModeLine)
        self.dockTools.actionModePolygon.triggered.connect(self.setModePolygon)

    def testEdFunc(self):
        print(self.dockTools.edFunc.text())

    def setModePoint(self):
        print("testPoint")
        self.view.current_tool = "Point"

    def setModeLine(self):
        print("testLine")
        self.view.current_tool = "Segment"

    def setModePolygon(self):
        print("testPolygon")
        self.view.current_tool = "Polygon"
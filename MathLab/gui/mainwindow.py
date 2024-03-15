from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from MathLab.gui.custom_graphics_view import CustomGraphicsView
from MathLab.gui.canvas import Canvas


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
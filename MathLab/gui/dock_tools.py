from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QToolButton, QActionGroup, QAction, QSizePolicy, QLineEdit
from PyQt5.QtCore import Qt

class DockTools(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tools")

        self.edFunc = QLineEdit(self)

        self.actionModePoint = QAction("Point", self)
        self.actionModePoint.setCheckable(True)
        self.actionModePoint.setToolTip("Set mode Point")
        self.actionModePoint.setStatusTip("Set mode Point")

        self.actionModeLine = QAction("Line", self)
        self.actionModeLine.setCheckable(True)
        self.actionModeLine.setToolTip("Set mode Line")
        self.actionModeLine.setStatusTip("Set mode Line")

        self.actionModePolygon = QAction("Polygon", self)
        self.actionModePolygon.setCheckable(True)
        self.actionModePolygon.setToolTip("Set mode Polygon")
        self.actionModePolygon.setStatusTip("Set mode Polygon")

        self.grpMode = QActionGroup(self)
        self.grpMode.addAction(self.actionModePoint)
        self.grpMode.addAction(self.actionModeLine)
        self.grpMode.addAction(self.actionModePolygon)


        self.wgt = QWidget(self)
        self.lay = QVBoxLayout(self.wgt)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        self.wgt.setLayout(self.lay)

        self.lay.addWidget(self.edFunc)

        self.btnPoint = QToolButton()
        self.btnPoint.setDefaultAction(self.actionModePoint)
        self.btnPoint.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.lay.addWidget(self.btnPoint)

        self.btnLine = QToolButton()
        self.btnLine.setDefaultAction(self.actionModeLine)
        self.btnLine.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.lay.addWidget(self.btnLine)

        self.btnPolygon = QToolButton()
        self.btnPolygon.setDefaultAction(self.actionModePolygon)
        self.btnPolygon.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.lay.addWidget(self.btnPolygon)

        self.lay.addStretch()

        self.setWidget(self.wgt)

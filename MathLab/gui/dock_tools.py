from PyQt5.QtWidgets import QDockWidget, QHBoxLayout, QVBoxLayout, QWidget, QToolButton, QActionGroup, QAction, QSizePolicy, \
    QLineEdit, QPushButton
from PyQt5.QtCore import Qt


class DockTools(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tools")
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)  # Убирает кнопку закрытия
        self.setMinimumWidth(200)

        self.grpMode = QActionGroup(self)

        self.wgt = QWidget(self)
        self.lay = QVBoxLayout(self.wgt)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)

        self.btnAddEdFunc = QPushButton("Add Function", self)
        self.lay.addWidget(self.btnAddEdFunc)
        
        self.layEdFuncs = QVBoxLayout(self.wgt)
        self.layEdFuncs.setContentsMargins(0, 0, 0, 0)
        self.layEdFuncs.setSpacing(0)
        self.lay.addLayout(self.layEdFuncs)

        self.tools = [
            {"name": "Move", "tooltip": "Set mode move", "statusTip": "Set mode Move"},
            {"name": "Eraser", "tooltip": "Set mode eraser", "statusTip": "Set mode Eraser"},
            {"name": "Point", "tooltip": "Set mode Point", "statusTip": "Set mode Point"},
            {"name": "Midpoint", "tooltip": "Set mode Midpoint", "statusTip": "Set mode Midpoint"},
            {"name": "Segment", "tooltip": "Set mode Segment", "statusTip": "Set mode Segment"},
            {"name": "Line", "tooltip": "Set mode Line", "statusTip": "Set mode Line"},
            {"name": "Parallel Line", "tooltip": "Set mode Parallel Line", "statusTip": "Set mode Parallel Line"},
            {"name": "Perpendicular Line", "tooltip": "Set mode Perpendicular Line",
             "statusTip": "Set mode Perpendicular Line"},
            {"name": "Perpendicular Bisector", "tooltip": "Set mode Perpendicular Bisector",
             "statusTip": "Set mode Perpendicular Bisector"},
            {"name": "Angle Bisector", "tooltip": "Set mode Angle Bisector", "statusTip": "Set mode Angle Bisector"},
            {"name": "Ray", "tooltip": "Set mode Ray", "statusTip": "Set mode Ray"},
            {"name": "Polygon", "tooltip": "Set mode Polygon", "statusTip": "Set mode Polygon"},
            {"name": "Circle", "tooltip": "Set mode Circle", "statusTip": "Set mode Circle"},
            {"name": "Distance", "tooltip": "Set mode distance", "statusTip": "Set mode Distance"},
        ]

        for tool in self.tools:
            self.add_tool(tool)

        self.lay.addStretch()
        self.setWidget(self.wgt)

    def initEnablesTools(self, disableList):
        actions = self.grpMode.actions()
        for action in actions:
            action.setDisabled(action.text() in disableList)

    def addEdFunc(self):
        ed = QLineEdit(self)
        ed.setMinimumHeight(30)
        hLay = QHBoxLayout()
        hLay.setContentsMargins(0, 0, 0, 0)
        hLay.setSpacing(0)
        hLay.addWidget(ed)
        
        btn = QToolButton()
        btn.setText("x")
        hLay.addWidget(btn)
        
        self.layEdFuncs.addLayout(hLay)
        return {"ed": ed, "btn": btn}

    def add_tool(self, tool_info):
        action = QAction(tool_info["name"], self)
        action.setCheckable(True)
        action.setToolTip(tool_info["tooltip"])
        action.setStatusTip(tool_info["statusTip"])
        self.grpMode.addAction(action)

        self.create_tool_button(action)

    def create_tool_button(self, action, height=30):
        button = QToolButton()
        button.setDefaultAction(action)
        button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        button.setMinimumHeight(height)
        self.lay.addWidget(button)

    def set_active_tool(self, tool_name):
        for action in self.grpMode.actions():
            if action.text() == tool_name:
                action.setChecked(True)
                break

    def connect_actions(self, tool_selected_callback):
        for action in self.grpMode.actions():
            action.triggered.connect(lambda checked, a=action: tool_selected_callback(a.text()))

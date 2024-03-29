from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QWidget, QToolButton, QActionGroup, QAction, QSizePolicy, QLineEdit
from PyQt5.QtCore import Qt

class DockTools(QDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tools")
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)  # Убирает кнопку закрытия
        self.setMinimumWidth(200)

        self.edFunc = QLineEdit(self)
        self.edFunc.setMinimumHeight(30)

        self.grpMode = QActionGroup(self)

        self.wgt = QWidget(self)
        self.lay = QVBoxLayout(self.wgt)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        self.lay.addWidget(self.edFunc)

        self.tools = [
            {"name": "Point", "tooltip": "Set mode Point", "statusTip": "Set mode Point"},
            {"name": "Segment", "tooltip": "Set mode Segment", "statusTip": "Set mode Segment"},
            {"name": "Line", "tooltip": "Set mode Line", "statusTip": "Set mode Line"},
            {"name": "Ray", "tooltip": "Set mode Ray", "statusTip": "Set mode Ray"},
            {"name": "Polygon", "tooltip": "Set mode Polygon", "statusTip": "Set mode Polygon"},
            {"name": "Circle", "tooltip": "Set mode Circle", "statusTip": "Set mode Circle"},
        ]

        for tool in self.tools:
            self.add_tool(tool)

        self.lay.addStretch()
        self.setWidget(self.wgt)

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

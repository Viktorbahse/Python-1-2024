from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtGui import QColor


class UndoRedoButton(QPushButton):
    def __init__(self, parent, view, command):
        super().__init__(parent)
        self.view = view
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0;
                margin-top: -10px;
                font-size: 45px;
                text-align: center;
                color: rgba(157, 161, 170, 255);
            }

            QPushButton:pressed {
                color: rgba(104, 110, 122, 255);
            }
        """)

        if command == "undo":
            self.setText("⤺")
            self.clicked.connect(self.on_undo_clicked)
        elif command == "redo":
            self.setText("⤻")
            self.clicked.connect(self.on_redo_clicked)

    def on_undo_clicked(self):
        self.view.undo_last_command()

    def on_redo_clicked(self):
        self.view.redo_last_command()

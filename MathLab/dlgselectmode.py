import sys

from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QApplication
from PyQt5.QtCore import pyqtSignal, QObject
from dlgselectlevel import DlgSelectLevel


class DlgSelectMode(QDialog):
    taskSelected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Mode")
        lay = QGridLayout()
        self.setLayout(lay)

        self.btnGame = QPushButton("GAME", self)
        lay.addWidget(self.btnGame, 0, 0)
        self.btnGame.clicked.connect(self.onGameClicked)

        self.btnWork = QPushButton("WORK", self)
        lay.addWidget(self.btnWork, 0, 1)
        self.btnWork.clicked.connect(self.onWorkClicked)

        self.btnQuit = QPushButton("QUIT", self)
        lay.addWidget(self.btnQuit, 1, 0, 1, 2)
        self.btnQuit.clicked.connect(self.onQuitClicked)

    def onGameClicked(self):
        self.modeGame = True

        dlg = DlgSelectLevel()
        if dlg.exec():
            self.taskSelected.emit(dlg)
            pass
        else:
            print(":(((")

        self.accept()
    def onWorkClicked(self):
        self.modeGame = False
        self.accept()

    def onQuitClicked(self):
        sys.exit(0)




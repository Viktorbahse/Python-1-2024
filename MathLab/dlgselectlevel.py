import sys
import configparser

from PyQt5.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QPushButton, QApplication, QToolBox, QTextEdit, \
    QDialogButtonBox, \
    QWidget, QToolButton, QSizePolicy


class DlgSelectLevel(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Level")
        lay = QGridLayout()
        self.setLayout(lay)

        self.currentLevel = -1
        self.currentInstruction = ""
        self.currentFileName = ""

        self.toolbox = QToolBox()
        self.textEdit = QTextEdit()
        self.dialogButtonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.dialogButtonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept)

        lay.addWidget(self.toolbox, 0, 0)
        lay.addWidget(self.textEdit, 0, 1)
        lay.addWidget(self.dialogButtonBox, 1, 0, 1, 2)

        self.toolbox.addItem(self.createPageButtons([
            {"level": 1, "instruction": "Постройте прямую, проходящую через две точки",          "filename": "task01_01"},
            {"level": 2, "instruction": "Постройте окружность, проходящую через заданную точку, с центром в начале координат", "filename": "task01_02"},
            {"level": 3, "instruction": "Постройте середину отрезка",          "filename": "task01_03"}
        ]), "Обучение")
        self.toolbox.addItem(self.createPageButtons([
            {"level": 11, "instruction": "Постройте прямую, перпендикулярную данной, проходящую через заданную точку", "filename": "task02_01"},
            {"level": 12, "instruction": "Постройте прямую, перпендикулярную данной, проходящую через заданную точку", "filename": "task02_02"},
            {"level": 13, "instruction": "Постройте луч, делящий угол пополам",          "filename": "task02_03"}
        ]), "7 класс")

    def loadListWins(self):
        config = configparser.ConfigParser()
        config.read('MathLab.ini')
        m = config['DEFAULT']
        if 'list_wins' in m.keys():
            s = config['DEFAULT']['list_wins']
            return s.strip('[]').replace(' ', '').split(',')
        return []

    def createPageButtons(self, pageDef):
        wgt = QWidget(self)
        lay = QVBoxLayout(wgt)
        lay.setContentsMargins(0, 0, 0, 0)
        # wgt.setLayout(lay)

        i = 1
        for page in pageDef:
            btn = QToolButton(wgt)
            btn.setText(str(i))
            level = page['level']
            listWins = self.loadListWins()
            if str(level) in listWins:
                btn.setStyleSheet("background-color: rgb(0, 255, 0);")
            else:
                btn.setStyleSheet("")

            lay.addWidget(btn)
            btn.setProperty("level", level)
            btn.setProperty("instruction", pageDef[i - 1]["instruction"])
            btn.setProperty("filename", pageDef[i - 1]["filename"])
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(self.onBtnLevelClicked)
            i = i + 1

        return wgt

    def onBtnLevelClicked(self):
        btn = self.sender()
        self.currentLevel = btn.property("level")
        self.currentInstruction = btn.property("instruction")
        self.currentFileName = btn.property("filename")
        self.textEdit.setText(self.currentInstruction)

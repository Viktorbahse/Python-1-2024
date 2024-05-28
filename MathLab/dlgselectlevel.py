import sys

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
            {"instruction": "1_text",          "filename": "task01_01"},
            {"instruction": "2_text_описание", "filename": "task1-2"},
            {"instruction": "3_text",          "filename": "task1-3"}
        ]), "Page1")
        self.toolbox.addItem(self.createPageButtons([
            {"instruction": "4_text",          "filename": "task2-1"},
            {"instruction": "5_text_описание", "filename": "task2-2"},
            {"instruction": "6_text",          "filename": "task2-3"}
        ]), "Page2")

        # self.toolbox.setCurrentIndex(1)
        # self.textEdit.setText("6_text")


    # def onBtnOkClicked(self):
    #     self.accept()
    def createPageButtons(self, pageDef):
        wgt = QWidget(self)
        lay = QVBoxLayout(wgt)
        lay.setContentsMargins(0, 0, 0, 0)
        # wgt.setLayout(lay)

        i = 1
        for page in pageDef:
            btn = QToolButton(wgt)
            btn.setText(str(i))
            lay.addWidget(btn)
            btn.setProperty("level", i)
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

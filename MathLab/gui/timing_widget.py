from PyQt5.QtWidgets import QLabel


class TimingWidget(QLabel):
    def __init__(self, parent=None):
        super(TimingWidget, self).__init__(parent)
        self.setText("*sb forbade me to use emoticons*")
        self.style()

    def style(self):
        # Красивое отображение
        self.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #3e5f8a;
                font-family: 'Aptos';
                border: 2px solid #9db1cc;
                background-color: #f0f8ff;
            }
        """)
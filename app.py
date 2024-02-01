import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox
from url_prep import url_prep, model
import pandas as pd


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(1000, 800)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 63, 21))
        self.setPalette(palette)

        self.setWindowTitle('Phishing Detection')
        self.setStyleSheet("QMainWindow {background-color: black; color: white;}")
        layout = QVBoxLayout()

        group_box = QGroupBox('Enter the URL:')
        group_layout = QVBoxLayout()

        group_box.setFixedSize(800, 200)
        group_box.setStyleSheet("color: white; font-size: 24px; ")
        layout.addWidget(group_box, alignment=Qt.AlignHCenter | Qt.AlignTop)

        self.lineEdit = QLineEdit()
        font = QFont()
        font.setPointSize(18)
        self.lineEdit.setStyleSheet("color: black;")
        self.lineEdit.setFont(font)
        self.lineEdit.setFixedHeight(60)
        self.lineEdit.setFixedWidth(700)
        group_layout.addWidget(self.lineEdit, alignment=Qt.AlignHCenter)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        button_layout = QHBoxLayout()

        self.btn = QPushButton('Submit')
        self.btn.clicked.connect(self.on_click)
        self.btn.setFixedWidth(200)
        self.btn.setFixedHeight(100)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setStyleSheet(
            "QPushButton {color: white; border-radius: 50px; background-color: black; border: 2px solid white;}"
            "QPushButton:hover {background-color: gray;}")
        button_layout.addWidget(self.btn)

        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self.on_clear)
        self.clear_btn.setFixedWidth(200)
        self.clear_btn.setFixedHeight(100)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet(
            "QPushButton {color: white; border-radius: 50px; background-color: black; border: 2px solid white;}"
            "QPushButton:hover {background-color: gray;}")
        button_layout.addWidget(self.clear_btn)

        layout.addLayout(button_layout)

        self.label = QLabel('Prediction: ')
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def on_click(self):
        try:
            text = self.lineEdit.text()
            url, error = url_prep(text)
            url_df = pd.DataFrame([url])
            prediction = model.predict(url_df)

            if prediction[0] == 0:
                result = "Legitimate"
            else:
                result = "Phishing"
            if error != "":
                self.label.setText(
                    f'Prediction: {result}\nRequest error occurred. Results may not be reliable. Consider this as a phishing website')
            else:
                self.label.setText(f'Prediction: {result}')

        except Exception as e:
            self.label.setText(f'Error: {e}')

    def on_clear(self):
        self.lineEdit.clear()
        self.label.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

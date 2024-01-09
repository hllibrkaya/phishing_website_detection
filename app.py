import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from url_prep import url_prep, model
import pandas as pd


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Phishing detection')
        layout = QVBoxLayout()

        self.label = QLabel('Enter the URL:')
        layout.addWidget(self.label)

        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit)

        self.btn = QPushButton('Submit')
        self.btn.clicked.connect(self.on_click)
        layout.addWidget(self.btn)

        self.clear_btn = QPushButton('Clear')
        self.clear_btn.clicked.connect(self.on_clear)
        layout.addWidget(self.clear_btn)

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
                self.label.setText(f'Error: {error}')

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

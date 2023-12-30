import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

class WebPageChecker(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.url_label = QLabel('Enter the URL to check:')
        layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.check_button = QPushButton('Check')
        self.check_button.clicked.connect(self.check_webpage)
        layout.addWidget(self.check_button)

        self.result_label = QLabel('')
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def check_webpage(self):
        url = self.url_input.text()
        self.view = QWebEngineView()
        self.view.load(QUrl(url))
        self.view.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok):
        if ok:
            self.result_label.setText('Web page is reachable.')
        else:
            self.result_label.setText('Web page is not reachable.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = WebPageChecker()
    main_window.show()
    sys.exit(app.exec_())
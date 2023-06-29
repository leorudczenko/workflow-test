import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)


class HelloWorld(QApplication):
    def __init__(self, args, testing_mode: bool = False):
        super().__init__(args)
        self.window = Window()
        if testing_mode:
            self.window.setAttribute(Qt.WA_DontShowOnScreen, True)
        else:
            self.window.show()
            sys.exit(self.exec())


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label_hide = True
        self.default_message = "Halloo World!"
        self.setWindowTitle("Hallo World")
        self.setup_widgets()

    def setup_widgets(self) -> None:
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.text_label = QLabel("")
        self.layout.addWidget(self.text_label)
        self.toggle_button = QPushButton("Toggle Message", self)
        self.layout.addWidget(self.toggle_button)
        self.toggle_button.clicked.connect(self.toggle_message)

    def toggle_message(self) -> None:
        if self.label_hide:
            self.text_label.setText(self.default_message)
            self.label_hide = False
        else:
            self.text_label.setText("")
            self.label_hide = True


if __name__ == "__main__":
    HelloWorld(sys.argv)

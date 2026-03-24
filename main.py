import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.ui.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)

    font = QFont("Times New Roman", 10)
    app.setFont(font)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

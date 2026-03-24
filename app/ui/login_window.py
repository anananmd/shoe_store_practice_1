from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.auth_service import authenticate, get_guest_user
from app.ui.products_window import ProductsWindow


class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Магазин обуви — Вход")
        self.setMinimumWidth(420)

        self.current_user = None
        self.products_window = None

        self.title_label = QLabel("Вход в систему")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Войти")
        self.guest_button = QPushButton("Войти как гость")

        self.login_button.clicked.connect(self.handle_login)
        self.guest_button.clicked.connect(self.handle_guest_login)

        form_layout = QFormLayout()
        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.guest_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def handle_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль.")
            return

        user = authenticate(username, password)

        if user is None:
            QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль.")
            return

        self.current_user = user
        self.open_products_window()

    def handle_guest_login(self) -> None:
        self.current_user = get_guest_user()
        self.open_products_window()

    def open_products_window(self) -> None:
        self.products_window = ProductsWindow(self.current_user)
        self.products_window.show()
        self.close()

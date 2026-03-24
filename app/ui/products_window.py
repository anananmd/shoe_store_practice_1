from pathlib import Path
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.product_service import (
    add_product,
    delete_product,
    get_all_products,
    get_all_suppliers,
    get_product_by_id,
    update_product,
)
from app.ui.orders_window import OrdersWindow
from app.ui.product_form import ProductForm


IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "resources" / "images"
PLACEHOLDER = IMAGES_DIR / "picture.png"
DB_PATH = Path(__file__).resolve().parent.parent.parent / "database" / "shoe_store.db"


def format_pairs(count: int) -> str:
    last_two = count % 100
    last_one = count % 10

    if 11 <= last_two <= 14:
        word = "пар"
    elif last_one == 1:
        word = "пара"
    elif last_one in (2, 3, 4):
        word = "пары"
    else:
        word = "пар"

    return f"{count} {word}"


class ProductItemWidget(QWidget):
    def __init__(self, product: dict) -> None:
        super().__init__()

        layout = QHBoxLayout()

        image_label = QLabel()
        image_label.setFixedSize(120, 120)

        image_path = product["image_path"]
        full_path = IMAGES_DIR / image_path if image_path else PLACEHOLDER

        if not full_path.exists():
            full_path = PLACEHOLDER

        pixmap = QPixmap(str(full_path))
        image_label.setPixmap(
            pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        info_layout = QVBoxLayout()

        name_label = QLabel(f"<b>{product['name']}</b>")

        price = product["price"]
        discount = product["discount_percent"]
        final_price = price * (1 - discount / 100)

        price_label = QLabel(
            f"Цена: {price:.2f} | Скидка: {discount:.0f}% | Итог: {final_price:.2f}"
        )
        stock_label = QLabel(
            f"Остаток: {format_pairs(product['quantity_in_stock'])}"
        )

        info_layout.addWidget(name_label)
        info_layout.addWidget(price_label)
        info_layout.addWidget(stock_label)

        layout.addWidget(image_label)
        layout.addLayout(info_layout)

        self.setLayout(layout)


class ProductsWindow(QWidget):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.user = user
        self.cart = []

        self.setWindowTitle("Магазин обуви — Товары")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        title = QLabel("Список товаров")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию товара...")
        self.search_input.textChanged.connect(self.load_products)

        self.supplier_filter = QComboBox()
        self.supplier_filter.addItem("Все поставщики")
        self.supplier_filter.addItems(get_all_suppliers())
        self.supplier_filter.currentTextChanged.connect(self.load_products)

        self.sort_box = QComboBox()
        self.sort_box.addItems(
            [
                "Без сортировки",
                "Остаток по возрастанию",
                "Остаток по убыванию",
            ]
        )
        self.sort_box.currentTextChanged.connect(self.load_products)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(self.supplier_filter)
        controls_layout.addWidget(self.sort_box)

        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.orders_button = QPushButton("Заказы")
        self.cart_button = QPushButton("В корзину")
        self.checkout_button = QPushButton("Оформить заказ")

        self.add_button.clicked.connect(self.handle_add_product)
        self.edit_button.clicked.connect(self.handle_edit_product)
        self.delete_button.clicked.connect(self.handle_delete_product)
        self.orders_button.clicked.connect(self.open_orders)
        self.cart_button.clicked.connect(self.add_to_cart)
        self.checkout_button.clicked.connect(self.checkout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.orders_button)
        buttons_layout.addWidget(self.cart_button)
        buttons_layout.addWidget(self.checkout_button)

        self.products_list = QListWidget()

        layout.addLayout(controls_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.products_list)
        self.setLayout(layout)

        self.apply_role_permissions()
        self.load_products()

    def apply_role_permissions(self) -> None:
        role = self.user["role"]

        if role in ("guest", "client"):
            self.add_button.setEnabled(False)
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.add_button.hide()
            self.edit_button.hide()
            self.delete_button.hide()

        elif role == "manager":
            self.delete_button.setEnabled(False)

    def add_to_cart(self) -> None:
        product_id = self.get_selected_product_id()
        if product_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return

        self.cart.append(product_id)

        QMessageBox.information(
            self,
            "Корзина",
            f"Товар добавлен. В корзине: {len(self.cart)}",
        )

    def load_products(self) -> None:
        self.products_list.clear()

        search_text = self.search_input.text().strip().lower()
        selected_supplier = self.supplier_filter.currentText()
        selected_sort = self.sort_box.currentText()

        products = get_all_products()
        filtered_products = []

        for product in products:
            if search_text and search_text not in product["name"].lower():
                continue

            if (
                selected_supplier != "Все поставщики"
                and product["supplier_name"] != selected_supplier
            ):
                continue

            filtered_products.append(product)

        if selected_sort == "Остаток по возрастанию":
            filtered_products.sort(key=lambda item: item["quantity_in_stock"])
        elif selected_sort == "Остаток по убыванию":
            filtered_products.sort(
                key=lambda item: item["quantity_in_stock"],
                reverse=True,
            )

        for product in filtered_products:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, product["id"])

            widget = ProductItemWidget(product)

            if product["quantity_in_stock"] == 0:
                item.setBackground(Qt.cyan)
            elif product["discount_percent"] > 15:
                item.setBackground(Qt.green)

            item.setSizeHint(widget.sizeHint())

            self.products_list.addItem(item)
            self.products_list.setItemWidget(item, widget)

    def get_selected_product_id(self) -> int | None:
        item = self.products_list.currentItem()
        if item is None:
            return None
        return item.data(Qt.UserRole)

    def handle_add_product(self) -> None:
        form = ProductForm()
        if form.exec():
            add_product(form.get_data())
            self.load_products()

    def handle_edit_product(self) -> None:
        product_id = self.get_selected_product_id()
        if product_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return

        product = get_product_by_id(product_id)
        form = ProductForm(product)

        if form.exec():
            update_product(product_id, form.get_data())
            self.load_products()

    def handle_delete_product(self) -> None:
        product_id = self.get_selected_product_id()
        if product_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return

        if not delete_product(product_id):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нельзя удалить товар, который есть в заказах",
            )
            return

        self.load_products()

    def checkout(self) -> None:
        if not self.cart:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return

        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO orders (order_date, customer_name, status) VALUES (?, ?, ?)",
            (
                "2026-01-01",
                self.user.get("username", "guest"),
                "new",
            ),
        )

        order_id = cursor.lastrowid

        for product_id in self.cart:
            cursor.execute(
                """
                SELECT price
                FROM products
                WHERE id = ?
                """,
                (product_id,),
            )
            row = cursor.fetchone()

            if row is None:
                continue

            cursor.execute(
                """
                INSERT INTO order_items (
                    order_id,
                    product_id,
                    quantity,
                    price_at_order
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    product_id,
                    1,
                    row["price"],
                ),
            )

        connection.commit()
        connection.close()

        self.cart.clear()

        QMessageBox.information(self, "Готово", "Заказ оформлен")

    def open_orders(self) -> None:
        self.orders_window = OrdersWindow()
        self.orders_window.show()

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)

from app.utils.db import get_connection


class OrderItemsWindow(QWidget):
    def __init__(self, order_id: int):
        super().__init__()

        self.setWindowTitle(f"Состав заказа #{order_id}")
        self.resize(500, 400)

        layout = QVBoxLayout()

        title = QLabel(f"Товары в заказе №{order_id}")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

        self.load_items(order_id)

    def load_items(self, order_id: int):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT p.name, oi.quantity, oi.price_at_order
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            WHERE oi.order_id = ?
            """,
            (order_id,),
        )

        rows = cursor.fetchall()

        for row in rows:
            text = (
                f"{row['name']} | "
                f"Кол-во: {row['quantity']} | "
                f"Цена: {row['price_at_order']}"
            )
            self.list_widget.addItem(QListWidgetItem(text))

        connection.close()

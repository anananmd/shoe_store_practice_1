from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.order_service import get_all_orders
from app.ui.order_items_window import OrderItemsWindow


class OrdersWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Заказы")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        self.orders_list = QListWidget()

        layout.addWidget(QLabel("Список заказов"))
        layout.addWidget(self.orders_list)

        self.setLayout(layout)

        self.orders_list.itemDoubleClicked.connect(self.open_order_items)

        self.load_orders()

    def load_orders(self) -> None:
        self.orders_list.clear()

        orders = get_all_orders()

        for order in orders:
            text = (
                f"№{order['id']} | "
                f"{order['customer_name']} | "
                f"{order['order_date']} | "
                f"{order['status']} | "
                f"{order['manager_name']}"
            )

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, order["id"])
            self.orders_list.addItem(item)

    def open_order_items(self, item: QListWidgetItem) -> None:
        order_id = item.data(Qt.UserRole)

        self.items_window = OrderItemsWindow(order_id)
        self.items_window.show()

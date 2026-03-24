from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
)

from app.services.product_service import get_reference_data


class ProductForm(QDialog):
    def __init__(self, product: dict | None = None) -> None:
        super().__init__()
        self.product = product

        self.setWindowTitle("Товар")
        self.setMinimumWidth(400)

        self.article_input = QLineEdit()
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.image_path_input = QLineEdit()

        self.category_box = QComboBox()
        self.category_box.addItems(get_reference_data("categories"))

        self.manufacturer_box = QComboBox()
        self.manufacturer_box.addItems(get_reference_data("manufacturers"))

        self.supplier_box = QComboBox()
        self.supplier_box.addItems(get_reference_data("suppliers"))

        self.unit_box = QComboBox()
        self.unit_box.addItems(get_reference_data("units"))

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(1_000_000)
        self.price_input.setDecimals(2)

        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(100)
        self.discount_input.setDecimals(2)

        self.quantity_input = QSpinBox()
        self.quantity_input.setMaximum(1_000_000)

        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")

        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.addRow("Артикул:", self.article_input)
        form_layout.addRow("Название:", self.name_input)
        form_layout.addRow("Категория:", self.category_box)
        form_layout.addRow("Описание:", self.description_input)
        form_layout.addRow("Производитель:", self.manufacturer_box)
        form_layout.addRow("Поставщик:", self.supplier_box)
        form_layout.addRow("Цена:", self.price_input)
        form_layout.addRow("Скидка %:", self.discount_input)
        form_layout.addRow("Количество:", self.quantity_input)
        form_layout.addRow("Единица:", self.unit_box)
        form_layout.addRow("Имя файла картинки:", self.image_path_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

        if self.product is not None:
            self.fill_form()

    def fill_form(self) -> None:
        self.article_input.setText(self.product["article"])
        self.name_input.setText(self.product["name"])
        self.description_input.setText(self.product["description"] or "")
        self.image_path_input.setText(self.product["image_path"] or "")

        self.category_box.setCurrentText(self.product["category_name"])
        self.manufacturer_box.setCurrentText(self.product["manufacturer_name"])
        self.supplier_box.setCurrentText(self.product["supplier_name"])
        self.unit_box.setCurrentText(self.product["unit_name"])

        self.price_input.setValue(float(self.product["price"]))
        self.discount_input.setValue(float(self.product["discount_percent"]))
        self.quantity_input.setValue(int(self.product["quantity_in_stock"]))

    def validate_and_accept(self) -> None:
        if not self.article_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите артикул.")
            return

        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название товара.")
            return

        self.accept()

    def get_data(self) -> dict:
        return {
            "article": self.article_input.text().strip(),
            "name": self.name_input.text().strip(),
            "category_name": self.category_box.currentText(),
            "description": self.description_input.text().strip(),
            "manufacturer_name": self.manufacturer_box.currentText(),
            "supplier_name": self.supplier_box.currentText(),
            "price": float(self.price_input.value()),
            "discount_percent": float(self.discount_input.value()),
            "quantity_in_stock": int(self.quantity_input.value()),
            "unit_name": self.unit_box.currentText(),
            "image_path": self.image_path_input.text().strip(),
        }

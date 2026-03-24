from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from app.utils.db import get_connection


BASE_DIR = Path(__file__).resolve().parent.parent
IMPORT_DIR = BASE_DIR / "import_data"


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_number(value, default: float = 0.0) -> float:
    if pd.isna(value):
        return default

    text = str(value).strip().replace(",", ".")
    if not text:
        return default

    return float(text)


def normalize_int(value, default: int = 0) -> int:
    if pd.isna(value):
        return default

    text = str(value).strip()
    if not text:
        return default

    return int(float(text))


def normalize_date(value) -> str:
    if pd.isna(value):
        return ""

    try:
        dt = pd.to_datetime(value)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(value).strip()


def ensure_pickup_points_table() -> None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pickup_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL UNIQUE
        )
        """
    )

    connection.commit()
    connection.close()


def get_table_columns(table_name: str) -> list[str]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()

    connection.close()
    return [row["name"] for row in rows]


def clear_existing_data() -> None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM pickup_points")
    cursor.execute("DELETE FROM suppliers")
    cursor.execute("DELETE FROM manufacturers")
    cursor.execute("DELETE FROM categories")
    cursor.execute("DELETE FROM units")

    connection.commit()
    connection.close()


def ensure_roles() -> None:
    connection = get_connection()
    cursor = connection.cursor()

    required_roles = ["guest", "client", "manager", "admin"]

    for role_name in required_roles:
        cursor.execute(
            """
            INSERT OR IGNORE INTO roles (name)
            VALUES (?)
            """,
            (role_name,),
        )

    connection.commit()
    connection.close()


def get_role_id(role_name: str) -> int:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM roles
        WHERE name = ?
        """,
        (role_name,),
    )
    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise ValueError(f"Роль не найдена: {role_name}")

    return row["id"]


def import_users() -> None:
    file_path = IMPORT_DIR / "user_import.xlsx"
    df = pd.read_excel(file_path)

    role_mapping = {
        "администратор": "admin",
        "менеджер": "manager",
        "клиент": "client",
        "гость": "guest",
    }

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        role_ru = normalize_text(row["Роль сотрудника"]).lower()
        role_name = role_mapping.get(role_ru)

        if role_name is None:
            continue

        full_name = normalize_text(row["ФИО"])
        username = normalize_text(row["Логин"])
        password = normalize_text(row["Пароль"])

        if not full_name or not username or not password:
            continue

        role_id = get_role_id(role_name)

        cursor.execute(
            """
            INSERT INTO users (username, password, full_name, role_id)
            VALUES (?, ?, ?, ?)
            """,
            (username, password, full_name, role_id),
        )

    client_role_id = get_role_id("client")
    cursor.execute(
        """
        INSERT INTO users (username, password, full_name, role_id)
        VALUES (?, ?, ?, ?)
        """,
        ("client", "123", "Клиент", client_role_id),
    )

    connection.commit()
    connection.close()


def get_or_create_reference_id(cursor, table_name: str, name: str) -> int:
    cursor.execute(
        f"""
        SELECT id
        FROM {table_name}
        WHERE name = ?
        """,
        (name,),
    )
    row = cursor.fetchone()

    if row is not None:
        return row["id"]

    cursor.execute(
        f"""
        INSERT INTO {table_name} (name)
        VALUES (?)
        """,
        (name,),
    )
    return cursor.lastrowid


def import_products() -> None:
    file_path = IMPORT_DIR / "Tovar.xlsx"
    df = pd.read_excel(file_path)

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        article = normalize_text(row["Артикул"])
        name = normalize_text(row["Наименование товара"])
        unit_name = normalize_text(row["Единица измерения"])
        price = normalize_number(row["Цена"])
        supplier_name = normalize_text(row["Поставщик"])
        manufacturer_name = normalize_text(row["Производитель"])
        category_name = normalize_text(row["Категория товара"])
        discount_percent = normalize_number(row["Действующая скидка"])
        quantity_in_stock = normalize_int(row["Кол-во на складе"])
        description = normalize_text(row["Описание товара"])
        image_path = normalize_text(row["Фото"])

        if not article or not name:
            continue

        category_id = get_or_create_reference_id(cursor, "categories", category_name)
        manufacturer_id = get_or_create_reference_id(
            cursor,
            "manufacturers",
            manufacturer_name,
        )
        supplier_id = get_or_create_reference_id(cursor, "suppliers", supplier_name)
        unit_id = get_or_create_reference_id(cursor, "units", unit_name)

        cursor.execute(
            """
            INSERT INTO products (
                article,
                name,
                category_id,
                description,
                manufacturer_id,
                supplier_id,
                price,
                discount_percent,
                quantity_in_stock,
                unit_id,
                image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article,
                name,
                category_id,
                description,
                manufacturer_id,
                supplier_id,
                price,
                discount_percent,
                quantity_in_stock,
                unit_id,
                image_path,
            ),
        )

    connection.commit()
    connection.close()


def import_pickup_points() -> None:
    file_path = IMPORT_DIR / "Пункты выдачи_import.xlsx"
    df = pd.read_excel(file_path, header=None)

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        address = normalize_text(row.iloc[0])
        if not address:
            continue

        cursor.execute(
            """
            INSERT OR IGNORE INTO pickup_points (address)
            VALUES (?)
            """,
            (address,),
        )

    connection.commit()
    connection.close()


def get_pickup_point_id(cursor, address: str) -> Optional[int]:
    cursor.execute(
        """
        SELECT id
        FROM pickup_points
        WHERE address = ?
        """,
        (address,),
    )
    row = cursor.fetchone()

    if row is None:
        return None

    return row["id"]


def get_product_id_and_price_by_article(
    cursor,
    article: str,
) -> tuple[Optional[int], Optional[float]]:

    cursor.execute(
        """
        SELECT id, price
        FROM products
        WHERE article = ?
        """,
        (article,),
    )

    row = cursor.fetchone()

    if row is None:
        return None, None

    return row["id"], row["price"]


def parse_order_articles(raw_value: str) -> list[tuple[str, int]]:
    parts = [part.strip() for part in str(raw_value).split(",") if part.strip()]
    result = []

    index = 0
    while index < len(parts):
        article = parts[index]
        quantity = 1

        if index + 1 < len(parts):
            next_part = parts[index + 1]
            try:
                quantity = int(next_part)
                index += 2
            except ValueError:
                index += 1
        else:
            index += 1

        result.append((article, quantity))

    return result


def insert_order(cursor, order_data: dict, order_columns: list[str]) -> int:
    fields = []
    values = []

    comment_parts = []

    if "id" in order_columns:
        fields.append("id")
        values.append(order_data["id"])

    if "order_date" in order_columns:
        fields.append("order_date")
        values.append(order_data["order_date"])

    if "customer_name" in order_columns:
        fields.append("customer_name")
        values.append(order_data["customer_name"])

    if "status" in order_columns:
        fields.append("status")
        values.append(order_data["status"])

    if "manager_id" in order_columns:
        fields.append("manager_id")
        values.append(None)

    if "delivery_date" in order_columns:
        fields.append("delivery_date")
        values.append(order_data["delivery_date"])
    else:
        comment_parts.append(f"Дата доставки: {order_data['delivery_date']}")

    if "pickup_point_id" in order_columns:
        fields.append("pickup_point_id")
        values.append(order_data["pickup_point_id"])
    else:
        comment_parts.append(f"Адрес пункта выдачи: {order_data['pickup_address']}")

    if "pickup_code" in order_columns:
        fields.append("pickup_code")
        values.append(order_data["pickup_code"])
    else:
        comment_parts.append(f"Код получения: {order_data['pickup_code']}")

    if "comment" in order_columns:
        final_comment = "; ".join(comment_parts)
        fields.append("comment")
        values.append(final_comment)

    placeholders = ", ".join(["?"] * len(fields))
    fields_sql = ", ".join(fields)

    cursor.execute(
        f"""
        INSERT INTO orders ({fields_sql})
        VALUES ({placeholders})
        """,
        values,
    )

    return order_data["id"]


def import_orders() -> None:
    file_path = IMPORT_DIR / "Заказ_import.xlsx"
    df = pd.read_excel(file_path)

    order_columns = get_table_columns("orders")

    connection = get_connection()
    cursor = connection.cursor()

    for _, row in df.iterrows():
        order_id = normalize_int(row["Номер заказа"])
        raw_articles = normalize_text(row["Артикул заказа"])
        order_date = normalize_date(row["Дата заказа"])
        delivery_date = normalize_date(row["Дата доставки"])
        pickup_address = normalize_text(row["Адрес пункта выдачи"])
        customer_name = normalize_text(row["ФИО авторизированного клиента"])
        pickup_code = normalize_text(row["Код для получения"])
        status = normalize_text(row["Статус заказа"])

        pickup_point_id = get_pickup_point_id(cursor, pickup_address)

        order_data = {
            "id": order_id,
            "order_date": order_date,
            "delivery_date": delivery_date,
            "pickup_address": pickup_address,
            "pickup_point_id": pickup_point_id,
            "customer_name": customer_name,
            "pickup_code": pickup_code,
            "status": status,
        }

        insert_order(cursor, order_data, order_columns)

        parsed_items = parse_order_articles(raw_articles)

        for article, quantity in parsed_items:
            product_id, price = get_product_id_and_price_by_article(cursor, article)

            if product_id is None or price is None:
                print(f"Пропуск позиции заказа {order_id}: не найден артикул {article}")
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
                (order_id, product_id, quantity, price),
            )

    connection.commit()
    connection.close()


def main() -> None:
    ensure_pickup_points_table()
    ensure_roles()
    clear_existing_data()

    import_users()
    import_products()
    import_pickup_points()
    import_orders()

    print("Импорт завершён успешно")


if __name__ == "__main__":
    main()

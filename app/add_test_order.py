from app.utils.db import get_connection


def main() -> None:
    connection = get_connection()
    cursor = connection.cursor()

    # берем менеджера
    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        ("manager",),
    )
    manager_id = cursor.fetchone()["id"]

    # берем первый существующий товар
    cursor.execute(
        "SELECT id, price FROM products ORDER BY id LIMIT 1"
    )
    product_row = cursor.fetchone()

    if product_row is None:
        raise ValueError("Нет товаров в базе")

    product_id = product_row["id"]
    price = product_row["price"]

    # создаем заказ
    cursor.execute(
        """
        INSERT INTO orders (
            order_date,
            customer_name,
            status,
            manager_id,
            comment
        ) VALUES (?, ?, ?, ?, ?)
        """,
        ("2026-03-24", "Тестовый клиент", "Новый", manager_id, "Тест"),
    )

    order_id = cursor.lastrowid

    # добавляем товар в заказ
    cursor.execute(
        """
        INSERT INTO order_items (
            order_id,
            product_id,
            quantity,
            price_at_order
        ) VALUES (?, ?, ?, ?)
        """,
        (order_id, product_id, 2, price),
    )

    connection.commit()
    connection.close()

    print("OK: заказ добавлен")


if __name__ == "__main__":
    main()

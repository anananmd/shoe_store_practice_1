from app.utils.db import get_connection


def get_all_orders() -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            orders.id,
            orders.order_date,
            orders.customer_name,
            orders.status,
            users.full_name AS manager_name,
            orders.comment
        FROM orders
        LEFT JOIN users ON users.id = orders.manager_id
        ORDER BY orders.id DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "id": row["id"],
            "order_date": row["order_date"],
            "customer_name": row["customer_name"],
            "status": row["status"],
            "manager_name": row["manager_name"],
            "comment": row["comment"],
        }
        for row in rows
    ]


def get_order_items(order_id: int) -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            products.name,
            order_items.quantity,
            order_items.price_at_order
        FROM order_items
        JOIN products ON products.id = order_items.product_id
        WHERE order_items.order_id = ?
        """,
        (order_id,),
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "name": row["name"],
            "quantity": row["quantity"],
            "price": row["price_at_order"],
        }
        for row in rows
    ]

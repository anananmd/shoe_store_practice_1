from app.utils.db import get_connection


def get_all_products() -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            products.id,
            products.article,
            products.name,
            categories.name AS category_name,
            products.description,
            manufacturers.name AS manufacturer_name,
            suppliers.name AS supplier_name,
            products.price,
            products.discount_percent,
            products.quantity_in_stock,
            units.name AS unit_name,
            products.image_path
        FROM products
        JOIN categories ON categories.id = products.category_id
        JOIN manufacturers ON manufacturers.id = products.manufacturer_id
        JOIN suppliers ON suppliers.id = products.supplier_id
        JOIN units ON units.id = products.unit_id
        ORDER BY products.id
        """
    )

    rows = cursor.fetchall()
    connection.close()

    products = []
    for row in rows:
        products.append(
            {
                "id": row["id"],
                "article": row["article"],
                "name": row["name"],
                "category_name": row["category_name"],
                "description": row["description"],
                "manufacturer_name": row["manufacturer_name"],
                "supplier_name": row["supplier_name"],
                "price": row["price"],
                "discount_percent": row["discount_percent"],
                "quantity_in_stock": row["quantity_in_stock"],
                "unit_name": row["unit_name"],
                "image_path": row["image_path"],
            }
        )

    return products


def get_all_suppliers() -> list[str]:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM suppliers
        ORDER BY name
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [row["name"] for row in rows]


def get_reference_data(table_name: str) -> list[str]:
    allowed_tables = {
        "categories",
        "manufacturers",
        "suppliers",
        "units",
    }

    if table_name not in allowed_tables:
        raise ValueError("Недопустимое имя таблицы")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(f"SELECT name FROM {table_name} ORDER BY name")
    rows = cursor.fetchall()
    connection.close()

    return [row["name"] for row in rows]


def get_product_by_id(product_id: int) -> dict | None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            products.id,
            products.article,
            products.name,
            categories.name AS category_name,
            products.description,
            manufacturers.name AS manufacturer_name,
            suppliers.name AS supplier_name,
            products.price,
            products.discount_percent,
            products.quantity_in_stock,
            units.name AS unit_name,
            products.image_path
        FROM products
        JOIN categories ON categories.id = products.category_id
        JOIN manufacturers ON manufacturers.id = products.manufacturer_id
        JOIN suppliers ON suppliers.id = products.supplier_id
        JOIN units ON units.id = products.unit_id
        WHERE products.id = ?
        """,
        (product_id,),
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "article": row["article"],
        "name": row["name"],
        "category_name": row["category_name"],
        "description": row["description"],
        "manufacturer_name": row["manufacturer_name"],
        "supplier_name": row["supplier_name"],
        "price": row["price"],
        "discount_percent": row["discount_percent"],
        "quantity_in_stock": row["quantity_in_stock"],
        "unit_name": row["unit_name"],
        "image_path": row["image_path"],
    }


def _get_id_by_name(cursor, table_name: str, name: str) -> int:
    cursor.execute(
        f"SELECT id FROM {table_name} WHERE name = ?",
        (name,),
    )
    row = cursor.fetchone()
    if row is None:
        raise ValueError(f"Не найдено значение '{name}' в таблице {table_name}")
    return row["id"]


def add_product(product_data: dict) -> None:
    connection = get_connection()
    cursor = connection.cursor()

    category_id = _get_id_by_name(cursor, "categories", product_data["category_name"])
    manufacturer_id = _get_id_by_name(
        cursor,
        "manufacturers",
        product_data["manufacturer_name"],
    )
    supplier_id = _get_id_by_name(cursor, "suppliers", product_data["supplier_name"])
    unit_id = _get_id_by_name(cursor, "units", product_data["unit_name"])

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
            product_data["article"],
            product_data["name"],
            category_id,
            product_data["description"],
            manufacturer_id,
            supplier_id,
            product_data["price"],
            product_data["discount_percent"],
            product_data["quantity_in_stock"],
            unit_id,
            product_data["image_path"],
        ),
    )

    connection.commit()
    connection.close()


def update_product(product_id: int, product_data: dict) -> None:
    connection = get_connection()
    cursor = connection.cursor()

    category_id = _get_id_by_name(cursor, "categories", product_data["category_name"])
    manufacturer_id = _get_id_by_name(
        cursor,
        "manufacturers",
        product_data["manufacturer_name"],
    )
    supplier_id = _get_id_by_name(cursor, "suppliers", product_data["supplier_name"])
    unit_id = _get_id_by_name(cursor, "units", product_data["unit_name"])

    cursor.execute(
        """
        UPDATE products
        SET
            article = ?,
            name = ?,
            category_id = ?,
            description = ?,
            manufacturer_id = ?,
            supplier_id = ?,
            price = ?,
            discount_percent = ?,
            quantity_in_stock = ?,
            unit_id = ?,
            image_path = ?
        WHERE id = ?
        """,
        (
            product_data["article"],
            product_data["name"],
            category_id,
            product_data["description"],
            manufacturer_id,
            supplier_id,
            product_data["price"],
            product_data["discount_percent"],
            product_data["quantity_in_stock"],
            unit_id,
            product_data["image_path"],
            product_id,
        ),
    )

    connection.commit()
    connection.close()


def product_has_orders(product_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS count_value
        FROM order_items
        WHERE product_id = ?
        """,
        (product_id,),
    )
    row = cursor.fetchone()
    connection.close()

    return row["count_value"] > 0


def delete_product(product_id: int) -> bool:
    if product_has_orders(product_id):
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,),
    )

    connection.commit()
    connection.close()
    return True

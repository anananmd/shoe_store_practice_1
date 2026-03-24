import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "database" / "shoe_store.db"


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("ROLES:")
    cursor.execute("SELECT id, name FROM roles ORDER BY id;")
    for row in cursor.fetchall():
        print(row)

    print("\nUSERS:")
    cursor.execute("SELECT id, username, full_name, role_id FROM users ORDER BY id;")
    for row in cursor.fetchall():
        print(row)

    print("\nPRODUCTS:")
    cursor.execute(
        """
        SELECT id, article, name, price, discount_percent, quantity_in_stock
        FROM products
        ORDER BY id;
        """
    )
    for row in cursor.fetchall():
        print(row)

    connection.close()


if __name__ == "__main__":
    main()

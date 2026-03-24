from app.utils.db import get_connection


def main() -> None:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            users.id,
            users.username,
            users.full_name,
            roles.name AS role_name
        FROM users
        JOIN roles ON roles.id = users.role_id
        ORDER BY users.id
        """
    )

    rows = cursor.fetchall()

    for row in rows:
        print(
            row["id"],
            row["username"],
            row["full_name"],
            row["role_name"],
        )

    connection.close()


if __name__ == "__main__":
    main()

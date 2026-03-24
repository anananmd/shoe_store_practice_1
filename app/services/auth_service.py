from typing import Optional

from app.utils.db import get_connection


def authenticate(username: str, password: str) -> Optional[dict]:
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
        WHERE users.username = ? AND users.password = ?
        """,
        (username, password),
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "full_name": row["full_name"],
        "role": row["role_name"],
    }


def get_guest_user() -> dict:
    return {
        "id": None,
        "username": "guest",
        "full_name": "Гость",
        "role": "guest",
    }

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"

DB_PATH = DATABASE_DIR / "shoe_store.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
SEED_PATH = DATABASE_DIR / "seed.sql"


def main() -> None:
    print("PROJECT_ROOT =", PROJECT_ROOT)
    print("DATABASE_DIR =", DATABASE_DIR)
    print("SCHEMA_PATH =", SCHEMA_PATH, SCHEMA_PATH.exists())
    print("SEED_PATH =", SEED_PATH, SEED_PATH.exists())
    print("DB_PATH =", DB_PATH)

    if DB_PATH.exists():
        DB_PATH.unlink()

    connection = sqlite3.connect(DB_PATH)

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    seed_sql = SEED_PATH.read_text(encoding="utf-8")

    connection.executescript(schema_sql)
    connection.executescript(seed_sql)

    connection.commit()
    connection.close()

    print("Database created successfully")


if __name__ == "__main__":
    main()

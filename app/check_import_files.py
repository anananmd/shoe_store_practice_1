from pathlib import Path

import pandas as pd


IMPORT_DIR = Path(__file__).resolve().parent.parent / "import_data"


def main() -> None:
    file_names = [
        "Tovar.xlsx",
        "user_import.xlsx",
        "Заказ_import.xlsx",
        "Пункты выдачи_import.xlsx",
    ]

    for file_name in file_names:
        file_path = IMPORT_DIR / file_name
        print("=" * 80)
        print(file_name)

        df = pd.read_excel(file_path)
        print("Колонки:", list(df.columns))
        print(df.head(5).to_string(index=False))
        print()


if __name__ == "__main__":
    main()

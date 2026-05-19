from pathlib import Path
import sqlite3
import pandas as pd


def main():
    current_folder = Path(__file__).parent

    excel_path = current_folder / "data" / "smart_factory_mes_dataset.xlsx"
    database_path = current_folder / "smart_factory.db"

    if not excel_path.exists():
        raise FileNotFoundError(
            f"Could not find {excel_path}. "
            "Put smart_factory_mes_dataset.xlsx inside the data folder."
        )

    sheet_names = [
        "Production_Log",
        "Downtime_Log",
        "Machine_Master",
        "Defect_Log"
    ]

    conn = sqlite3.connect(database_path)

    for sheet_name in sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df.to_sql(sheet_name, conn, if_exists="replace", index=False)
        print(f"Loaded {sheet_name} -> {sheet_name}: {len(df)} rows")

    conn.close()

    print()
    print(f"SQLite database created successfully: {database_path}")


if __name__ == "__main__":
    main()
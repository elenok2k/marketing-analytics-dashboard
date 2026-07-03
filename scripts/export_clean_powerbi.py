import sqlite3
import pandas as pd
import os

DB_PATH = "data/marketing.db"
OUTPUT_DIR = "data/powerbi"

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

tables = [
    "campaigns",
    "campaign_marketing_metrics",
    "customers",
    "events",
    "products",
    "transactions",
    "efficiency_metrics",
    "cohort_analysis"
]

for table in tables:

    print(f"\n📤 Exporting {table}...")

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

        df = df.replace(["NULL", "null", "", "None"], None)


        for col in df.columns:

            if df[col].dtype == "object":

                df[col] = pd.to_numeric(df[col], errors="ignore")

        file_path = os.path.join(
            OUTPUT_DIR,
            f"{table}.csv"
        )

        df.to_csv(
            file_path,
            index=False,
            decimal=","   # 👈 КЛЮЧЕВО ДЛЯ РУССКОЙ ЛОКАЛИ
        )

    except Exception as e:
        print(f"Error in {table}: {e}")

conn.close()

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

        # -----------------------------
        # 1. CLEAN DATA
        # -----------------------------

        df = df.replace(["NULL", "null", "", "None"], None)

        # -----------------------------
        # 2. FORCE NUMERIC CONVERSION
        # -----------------------------

        for col in df.columns:

            if df[col].dtype == "object":

                df[col] = pd.to_numeric(df[col], errors="ignore")

        # -----------------------------
        # 3. EXPORT (ВАЖНО: decimal=",")
        # -----------------------------

        file_path = os.path.join(
            OUTPUT_DIR,
            f"{table}.csv"
        )

        df.to_csv(
            file_path,
            index=False,
            decimal=","   # 👈 КЛЮЧЕВО ДЛЯ РУССКОЙ ЛОКАЛИ
        )

        print(f"✅ Saved: {file_path}")
        print(f"   Rows: {len(df)} | Cols: {len(df.columns)}")

    except Exception as e:
        print(f"❌ Error in {table}: {e}")

conn.close()

print("\n🎉 EXPORT COMPLETED (RU LOCALE SAFE)")
# scripts/cohort_analysis_fixed.py
import sqlite3
import pandas as pd
import os

db_path = 'data/marketing.db'

if not os.path.exists(db_path):
    print(f"База данных не найдена: {db_path}")
    exit()

conn = sqlite3.connect(db_path)

conn.execute("DROP TABLE IF EXISTS cohort_analysis")

create_query = """
CREATE TABLE cohort_analysis AS
WITH first_purchase AS (
    SELECT 
        customer_id,
        MIN(timestamp) AS first_purchase_date
    FROM transactions
    GROUP BY customer_id
),
cohort_data AS (
    SELECT 
        f.customer_id,
        f.first_purchase_date,
        t.timestamp AS transaction_date,
        t.gross_revenue,
        t.transaction_id,
        strftime('%Y-%m', f.first_purchase_date) AS cohort_month
    FROM first_purchase f
    JOIN transactions t ON f.customer_id = t.customer_id
)
SELECT 
    cohort_month,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(transaction_id) AS total_orders,
    ROUND(SUM(gross_revenue), 2) AS total_revenue,
    ROUND(AVG(gross_revenue), 2) AS avg_order_value,
    ROUND(SUM(gross_revenue) / NULLIF(COUNT(DISTINCT customer_id), 0), 2) AS ltv_per_customer,
    ROUND(COUNT(transaction_id) * 1.0 / NULLIF(COUNT(DISTINCT customer_id), 0), 2) AS orders_per_customer
FROM cohort_data
GROUP BY cohort_month
ORDER BY cohort_month DESC
"""

conn.execute(create_query)

df = pd.read_sql_query("SELECT * FROM cohort_analysis ORDER BY cohort_month DESC", conn)
print(df.to_string(index=False))

stats_query = """
SELECT 
    COUNT(*) AS total_cohorts,
    SUM(customers) AS total_customers,
    ROUND(AVG(ltv_per_customer), 2) AS avg_ltv,
    ROUND(MAX(ltv_per_customer), 2) AS max_ltv,
    ROUND(MIN(ltv_per_customer), 2) AS min_ltv
FROM cohort_analysis
"""

stats = pd.read_sql_query(stats_query, conn)
print(stats.to_string(index=False))

top = pd.read_sql_query("""
SELECT 
    cohort_month,
    customers,
    ROUND(ltv_per_customer, 2) AS ltv,
    total_orders,
    orders_per_customer
FROM cohort_analysis
ORDER BY ltv_per_customer DESC
LIMIT 5
""", conn)
print(top.to_string(index=False))

conn.close()

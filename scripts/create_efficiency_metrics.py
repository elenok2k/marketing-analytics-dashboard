# scripts/create_efficiency_metrics.py
import sqlite3
import pandas as pd
import os

os.makedirs("exports", exist_ok=True)

db_path = "data/marketing.db"

if not os.path.exists(db_path):
    exit()

conn = sqlite3.connect(db_path)

conn.execute("DROP TABLE IF EXISTS efficiency_metrics")

create_query = """
CREATE TABLE efficiency_metrics AS
WITH campaign_performance AS (
    SELECT 
        c.channel,
        c.campaign_id,
        m.spend,
        m.impressions,
        m.clicks,
        c.expected_uplift,
        COUNT(DISTINCT t.customer_id) AS customers_acquired,
        COUNT(t.transaction_id) AS total_orders,
        SUM(t.gross_revenue) AS total_revenue,
        ROUND(AVG(t.gross_revenue), 2) AS avg_order_value,
        COUNT(DISTINCT e.session_id) AS sessions,
        COUNT(DISTINCT CASE 
            WHEN t.customer_id IN (
                SELECT customer_id 
                FROM transactions 
                GROUP BY customer_id 
                HAVING COUNT(transaction_id) > 1
            ) THEN t.customer_id 
        END) AS repeat_customers
    FROM campaigns c
    LEFT JOIN campaign_marketing_metrics m ON c.campaign_id = m.campaign_id
    LEFT JOIN transactions t ON c.campaign_id = t.campaign_id
    LEFT JOIN events e ON c.campaign_id = e.campaign_id AND t.customer_id = e.customer_id
    GROUP BY c.campaign_id
)
SELECT 
    channel,
    campaign_id,
    ROUND(spend, 2) AS spend,
    impressions,
    clicks,
    expected_uplift,
    customers_acquired,
    total_orders,
    ROUND(total_revenue, 2) AS revenue,
    avg_order_value,
    sessions,
    repeat_customers,
    ROUND(repeat_customers * 1.0 / NULLIF(customers_acquired, 0) * 100, 1) AS repeat_rate,
    ROUND(clicks * 1.0 / NULLIF(impressions, 0) * 100, 2) AS ctr,
    ROUND(spend / NULLIF(clicks, 0), 2) AS cpc,
    ROUND(customers_acquired * 1.0 / NULLIF(clicks, 0) * 100, 2) AS cvr,
    ROUND(spend / NULLIF(customers_acquired, 0), 2) AS cac,
    ROUND(total_revenue / NULLIF(customers_acquired, 0), 2) AS ltv,
    ROUND(total_revenue / NULLIF(spend, 0), 2) AS roas,
    ROUND((total_revenue - spend) / NULLIF(spend, 0) * 100, 1) AS romi_pct,
    ROUND((total_revenue / NULLIF(customers_acquired, 0)) / (spend / NULLIF(customers_acquired, 0)), 2) AS ltv_cac_ratio
FROM campaign_performance
ORDER BY roas DESC
"""

conn.execute(create_query)
conn.commit()


summary = pd.read_sql_query("""
SELECT 
    channel,
    COUNT(*) AS campaigns,
    ROUND(AVG(spend), 2) AS avg_spend,
    ROUND(AVG(revenue), 2) AS avg_revenue,
    ROUND(AVG(roas), 2) AS avg_roas,
    ROUND(AVG(romi_pct), 1) AS avg_romi,
    ROUND(AVG(cac), 2) AS avg_cac,
    ROUND(AVG(ltv), 2) AS avg_ltv,
    SUM(customers_acquired) AS total_customers
FROM efficiency_metrics
GROUP BY channel
ORDER BY avg_roas DESC
""", conn)

print(summary.to_string(index=False))

# Сохраняем в CSV
metrics = pd.read_sql_query("SELECT * FROM efficiency_metrics", conn)
metrics.to_csv("exports/efficiency_metrics.csv", index=False)

conn.close()

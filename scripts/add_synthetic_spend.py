# scripts/add_synthetic_spend.py
import sqlite3
import pandas as pd
import os

print("=" * 60)
print("📊 ГЕНЕРАЦИЯ РЕАЛИСТИЧНЫХ РАСХОДОВ (ROAS 1.0–2.0)")
print("=" * 60)

db_path = 'data/marketing.db'

if not os.path.exists(db_path):
    print(f"❌ База данных не найдена: {db_path}")
    exit()

conn = sqlite3.connect(db_path)

# Удаляем старую таблицу
conn.execute("DROP TABLE IF EXISTS campaign_marketing_metrics")

# Создаём новую с расходами 50–100% от выручки
print("\n📊 Создание таблицы campaign_marketing_metrics...")

create_query = """
CREATE TABLE campaign_marketing_metrics AS
WITH campaign_revenue AS (
    SELECT 
        c.campaign_id,
        c.channel,
        COALESCE(SUM(t.gross_revenue), 0) AS revenue
    FROM campaigns c
    LEFT JOIN transactions t ON c.campaign_id = t.campaign_id
    GROUP BY c.campaign_id
)
SELECT 
    cr.campaign_id,
    -- spend = 50–100% от выручки (ROAS будет 1.0–2.0)
    ROUND(
        CASE 
            WHEN cr.revenue > 1000 THEN 
                cr.revenue * (0.50 + ABS(RANDOM() % 50) / 100.0)
            ELSE 
                1000 + ABS(RANDOM() % 2000)
        END
    , 2) AS spend,
    
    -- impressions = spend × (15–30)
    CAST(
        ROUND(
            CASE 
                WHEN cr.revenue > 1000 THEN 
                    (cr.revenue * (0.50 + ABS(RANDOM() % 50) / 100.0)) * (15 + ABS(RANDOM() % 15))
                ELSE 
                    (1000 + ABS(RANDOM() % 2000)) * (15 + ABS(RANDOM() % 15))
            END
        , 0) AS INTEGER
    ) AS impressions,
    
    -- clicks = impressions × (1–4%)
    CAST(
        ROUND(
            CASE 
                WHEN cr.revenue > 1000 THEN 
                    (cr.revenue * (0.50 + ABS(RANDOM() % 50) / 100.0)) * (15 + ABS(RANDOM() % 15)) * (0.01 + ABS(RANDOM() % 3) / 100.0)
                ELSE 
                    (1000 + ABS(RANDOM() % 2000)) * (15 + ABS(RANDOM() % 15)) * (0.01 + ABS(RANDOM() % 3) / 100.0)
            END
        , 0) AS INTEGER
    ) AS clicks
FROM campaign_revenue cr
"""

conn.execute(create_query)
conn.commit()

print("✅ Таблица campaign_marketing_metrics создана!")

# Проверяем результат
print("\n📊 Проверка расходов по каналам:")

check_query = """
SELECT 
    c.channel,
    COUNT(*) AS campaigns,
    ROUND(AVG(m.spend), 2) AS avg_spend,
    ROUND(AVG(m.impressions), 0) AS avg_impressions,
    ROUND(AVG(m.clicks), 0) AS avg_clicks,
    ROUND(AVG(m.clicks) * 1.0 / NULLIF(AVG(m.impressions), 0) * 100, 2) AS avg_ctr
FROM campaigns c
JOIN campaign_marketing_metrics m ON c.campaign_id = m.campaign_id
GROUP BY c.channel
ORDER BY avg_spend DESC
"""

check_df = pd.read_sql_query(check_query, conn)
print(check_df.to_string(index=False))

# Проверяем ROAS
print("\n📊 Новый ROAS по каналам (должен быть 1.0–2.0):")

roas_query = """
SELECT 
    c.channel,
    ROUND(SUM(m.spend), 2) AS total_spend,
    ROUND(SUM(t.gross_revenue), 2) AS total_revenue,
    ROUND(SUM(t.gross_revenue) / NULLIF(SUM(m.spend), 0), 2) AS avg_roas
FROM campaigns c
LEFT JOIN campaign_marketing_metrics m ON c.campaign_id = m.campaign_id
LEFT JOIN transactions t ON c.campaign_id = t.campaign_id
GROUP BY c.channel
ORDER BY avg_roas DESC
"""

roas_df = pd.read_sql_query(roas_query, conn)
print(roas_df.to_string(index=False))

conn.close()

print("\n" + "=" * 60)
print("🎉 ГОТОВО!")
print("📊 Теперь ROAS должен быть в диапазоне 1.0–2.0")
print("📌 Запусти create_efficiency_metrics.py, чтобы пересчитать метрики.")
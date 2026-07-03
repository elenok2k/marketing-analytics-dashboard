# scripts/load_data.py
import sqlite3
import pandas as pd
import os

print("=" * 60)
print("📊 ЗАГРУЗКА ДАННЫХ В SQLITE")
print("=" * 60)

data_dir = 'data/raw/'

if not os.path.exists(data_dir):
    print(f"❌ Папка {data_dir} не найдена!")
    os.makedirs(data_dir, exist_ok=True)
    print(f"✅ Папка создана! Поместите CSV-файлы в {data_dir}")
    exit()

files = ['campaigns.csv', 'customers.csv', 'events.csv', 'products.csv', 'transactions.csv']
existing_files = [f for f in files if os.path.exists(os.path.join(data_dir, f))]

if not existing_files:
    print(f"❌ В папке {data_dir} нет CSV-файлов!")
    exit()

print(f"\n📁 Найдены файлы: {', '.join(existing_files)}")

conn = sqlite3.connect('data/marketing.db')

print("\n📥 Загрузка данных...")
print("-" * 40)

try:
    df = pd.read_csv(os.path.join(data_dir, 'campaigns.csv'))
    df.to_sql('campaigns', conn, if_exists='replace', index=False)
    print(f"   ✅ campaigns: {len(df)} записей")
    
    df = pd.read_csv(os.path.join(data_dir, 'customers.csv'))
    df.to_sql('customers', conn, if_exists='replace', index=False)
    print(f"   ✅ customers: {len(df)} записей")
    
    df = pd.read_csv(os.path.join(data_dir, 'events.csv'))
    df.to_sql('events', conn, if_exists='replace', index=False)
    print(f"   ✅ events: {len(df)} записей")
    
    df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
    df.to_sql('products', conn, if_exists='replace', index=False)
    print(f"   ✅ products: {len(df)} записей")
    
    df = pd.read_csv(os.path.join(data_dir, 'transactions.csv'))
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    print(f"   ✅ transactions: {len(df)} записей")
    
    print("\n✅ ВСЕ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ!")

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    conn.close()
    exit()

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print("\n📋 Таблицы в базе данных:")
print(tables.to_string(index=False))

conn.close()
print("\n🎉 БАЗА ДАННЫХ ГОТОВА К РАБОТЕ!")
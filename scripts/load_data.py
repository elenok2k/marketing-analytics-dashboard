# scripts/load_data.py
import sqlite3
import pandas as pd
import os

data_dir = 'data/raw/'

if not os.path.exists(data_dir):
    print(f"Папка {data_dir} не найдена!")
    os.makedirs(data_dir, exist_ok=True)
    exit()

files = ['campaigns.csv', 'customers.csv', 'events.csv', 'products.csv', 'transactions.csv']
existing_files = [f for f in files if os.path.exists(os.path.join(data_dir, f))]

if not existing_files:
    print(f"В папке {data_dir} нет CSV-файлов!")
    exit()


conn = sqlite3.connect('data/marketing.db')

try:
    df = pd.read_csv(os.path.join(data_dir, 'campaigns.csv'))
    df.to_sql('campaigns', conn, if_exists='replace', index=False)
    
    df = pd.read_csv(os.path.join(data_dir, 'customers.csv'))
    df.to_sql('customers', conn, if_exists='replace', index=False)
    
    df = pd.read_csv(os.path.join(data_dir, 'events.csv'))
    df.to_sql('events', conn, if_exists='replace', index=False)
    
    df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
    df.to_sql('products', conn, if_exists='replace', index=False)
    
    df = pd.read_csv(os.path.join(data_dir, 'transactions.csv'))
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    
except Exception as e:
    print(f"\nОШИБКА: {e}")
    conn.close()
    exit()

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)

print(tables.to_string(index=False))

conn.close()

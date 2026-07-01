import pandas as pd
import sqlite3
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # поднимаемся на уровень выше
data_raw_path = os.path.join(project_root, 'data', 'raw')

if not os.path.exists(data_raw_path):
    print(f" Папка не найдена: {data_raw_path}")
    print(" Создаю папку...")
    os.makedirs(data_raw_path, exist_ok=True)
    print(" Папка создана! Поместите CSV-файлы в неё.")
    exit()


csv_files = [f for f in os.listdir(data_raw_path) if f.endswith('.csv')]
print(f"\n Найдено CSV-файлов: {len(csv_files)}")
for f in csv_files:
    print(f"   - {f}")


data = {}
for file in csv_files:
    name = file.replace('.csv', '')
    file_path = os.path.join(data_raw_path, file)
    data[name] = pd.read_csv(file_path)
    print(f" Загружен {file} - {len(data[name])} записей")

db_path = os.path.join(project_root, 'data', 'marketing.db')
conn = sqlite3.connect(db_path)

for name, df in data.items():
    df.to_sql(name, conn, if_exists='replace', index=False)



print("\n Список таблиц в базе данных:")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
print(tables)

conn.close()

import sqlite3
import pandas as pd
import random

conn = sqlite3.connect('../data/marketing.db')

try:
    conn.execute("ALTER TABLE campaigns ADD COLUMN spend REAL")
    print(" Колонка spend добавлена")
except:
    print("ℹ Колонка spend уже существует")


try:
    conn.execute("ALTER TABLE campaigns ADD COLUMN impressions INTEGER")
    print(" Колонка impressions добавлена")
except:
    print("ℹ Колонка impressions уже существует")


try:
    conn.execute("ALTER TABLE campaigns ADD COLUMN clicks INTEGER")
    print(" Колонка clicks добавлена")
except:
    print("ℹ Колонка clicks уже существует")



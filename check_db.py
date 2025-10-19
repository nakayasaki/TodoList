import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

print("📋 作成済みテーブル一覧：")
for t in tables:
    print("-", t[0])

conn.close()

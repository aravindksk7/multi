import sqlite3

conn = sqlite3.connect('testtool.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:")
for table in tables:
    print(f"  - {table}")
conn.close()

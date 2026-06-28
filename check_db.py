import sqlite3

conn = sqlite3.connect('backend/copilot.db')
cursor = conn.cursor()

cursor.execute("SELECT id, status, repo_url, error_message, created_at FROM analyses ORDER BY created_at DESC LIMIT 10")
rows = cursor.fetchall()
print("Analyses rows:")
for r in rows:
    print(r)

conn.close()

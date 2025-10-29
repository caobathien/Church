import sqlite3
conn = sqlite3.connect('instance/students.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username, role FROM user')
rows = cursor.fetchall()
print('User table:')
for row in rows:
    print(row)
conn.close()

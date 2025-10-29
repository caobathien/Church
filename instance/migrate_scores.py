import sqlite3

# Kết nối đến database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Thêm các cột điểm số mới
alter_queries = [
    "ALTER TABLE student ADD COLUMN diem_mieng REAL DEFAULT 0.0;",
    "ALTER TABLE student ADD COLUMN diem_giua_ki_1 REAL DEFAULT 0.0;",
    "ALTER TABLE student ADD COLUMN diem_cuoi_ki_1 REAL DEFAULT 0.0;",
    "ALTER TABLE student ADD COLUMN diem_giua_ki_2 REAL DEFAULT 0.0;",
    "ALTER TABLE student ADD COLUMN diem_cuoi_ki_2 REAL DEFAULT 0.0;"
]

for query in alter_queries:
    try:
        cursor.execute(query)
        print(f"Executed: {query}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column already exists, skipping: {query}")
        else:
            print(f"Error executing {query}: {e}")

# Lưu thay đổi
conn.commit()
conn.close()

print("Migration completed!")
